from __future__ import with_statement

import logging
from contextlib import closing

from utils.file_utils import file2str_list, gen_open
from utils import to_utf8

logger = logging.getLogger('corpus.CorpusBase')
from text.blob import TextBlob
from cStringIO import StringIO
import gzip

filterTag = set(['DOCNO', 'FILEID', 'FIRST', 'SECOND', 'BYLINE', 'DATELINE'])


class Document():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.cached = False

    def __setitem__(self, key, item): self.__dict__[key] = item

    def __getitem__(self, key): return self.__dict__[key]

    def __str__(self):
        return str(self.__dict__)

    def cache_sentences(self):
        self.cached = True
        self.cache_list = []
        for key, value in self.__dict__.items():
            if key not in filterTag:
                try:
                    blob = TextBlob(value)
                    for sentence in blob.sentences:
                        self.cache_list.append(sentence)
                except Exception as e:
                    logger.debug("textblob error| %s:%s" % (key, value))

    def to_sentences(self):
        if self.cached:
            for sentence in self.cache_list:
                yield sentence
        else:
            for key, value in self.__dict__.items():
                if key not in filterTag:
                    try:
                        blob = TextBlob(value)
                        for sentence in blob.sentences:
                            yield sentence
                    except Exception as e:
                        logger.debug("textblob error| %s:%s" % (key, value))



class CorpusBase():
    """

    """
    def __init__(self, collection_spec=None):
        self.collection_spec = collection_spec
        self.collection_spec_list = file2str_list(collection_spec)

    def __iter__(self):
        """
        Iterate over the corpus, yielding one document at a time.
        """
        raise NotImplementedError('cannot instantiate abstract base class')


    def __len__(self):
        """
        Return the number of documents in the corpus.

        This method is just the least common denominator and should really be
        overridden when possible.
        """
        raise NotImplementedError("must override __len__() before calling len(corpus)")
#        logger.warning("performing full corpus scan to determine its length; was this intended?")
#        return sum(1 for doc in self) # sum(empty generator) == 0, so this works even for an empty corpus


def getstream(input):
    """
    If input is a filename (string), return `open(input)`.
    If input is a file-like object, reset it to the beginning with `input.seek(0)`.
    """
    assert input is not None
    if isinstance(input, basestring):
        # input was a filename: open as text file
        result = open(input)
    else:
        # input was a file-like object (BZ2, Gzip etc.); reset the stream to its beginning
        result = input
        result.seek(0)
    return result


import lucene
from org.apache.lucene.analysis.core import LowerCaseFilter, StopFilter, StopAnalyzer
from org.apache.lucene.analysis.en import PorterStemFilter
from org.apache.lucene.analysis.standard import StandardTokenizer, StandardFilter
from org.apache.pylucene.analysis import PythonAnalyzer
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from org.apache.lucene.util import Version
from java.io import StringReader

class PorterStemmerAnalyzer(PythonAnalyzer):
    def createComponents(self, fieldName, reader):
        source = StandardTokenizer(Version.LUCENE_CURRENT, reader)
        filter = StandardFilter(Version.LUCENE_CURRENT, source)
        filter = LowerCaseFilter(Version.LUCENE_CURRENT, filter)
        filter = PorterStemFilter(filter)
        filter = StopFilter(Version.LUCENE_CURRENT, filter,
        StopAnalyzer.ENGLISH_STOP_WORDS_SET)
        return self.TokenStreamComponents(source, filter)

lucene.initVM(vmargs=['-Djava.awt.headless=true'])
#lucene.initVM()

analyzer = PorterStemmerAnalyzer()

def testPorter():
    print('lucene', lucene.VERSION, lucene.CLASSPATH)
    input = 'this is a test string for Analyzer'
    analyzer = PorterStemmerAnalyzer()
    ts = analyzer.tokenStream("dummy", StringReader(input))
    ts.reset(); ##Resets this stream to the beginning. (Required
    while ts.incrementToken():
        #print ts.r
        #print ts.reflectAsString(True)
        print(termAtt.toString(), offsetAtt.startOffset(), offsetAtt.endOffset())



class TagCorpus(CorpusBase):
    """

    """
    def __init__(self, collection_spec=None, doctag='DOC', indextag=[], workers=2):
        CorpusBase.__init__(self, collection_spec=collection_spec)
        self.doctag = doctag
        self.indextag = indextag
        self.length = 0
        self.workers = workers
        from multiprocessing import Queue
        self.file_queue = Queue()


    def __iter__(self):
        """
        The function that defines a corpus.
        Iterating over the corpus must yield a document.
        """
        for job in self.collection_spec_list:
            self.file_queue.put_nowait(job)
        for _ in xrange(self.workers):
            self.file_queue.put(None)  # give the workers heads up that they can finish -- no more work!

        from multiprocessing import Queue, Process


        jobs = Queue(maxsize=1000 * self.workers)

        def worker_extract(pid):
            while True:
                fname = self.file_queue.get()
                if fname is None:  # data finished, exit
                    print('process %s is ending, with jobs size- %s' % (pid, jobs.qsize()))
                    break
                #print '%s handling: %s' % (pid, fname)
                with closing(gen_open(fname)) as f:
                    soup = BeautifulSoup('<docs>'+f.read()+'</docs>', 'xml')
                    docs = soup.find_all(self.doctag)
                    for dtag in docs:
                        retdoc = Document()
                        for child in dtag.children:
                            if isinstance(child, Tag):
                                retdoc[child.name] = child.text
                        retdoc.cache_sentences()  # to make it faster, hopefully
                        self.length += 1
                        jobs.put(retdoc)
        #p = Pool(self.workers)
        #print 'creating'
        #p.map_async(worker_extract, self.collection_spec_list)

        process_list = [Process(target=worker_extract, args=(i, )) for i in range(self.workers)]
        for p in process_list:
            p.daemon = True
            p.start()

        #print 'begin yield'
        num = 0
        while True:
            try:
                doc = jobs.get(timeout=5)
                num += 1
                yield doc
                if num % 10000 == 0:
                    print('jobs size:', jobs.qsize())
            except Exception as e:
                print(e.message)
                break
        for p in process_list:
            p.join()
        print('finished extracting documents, with jobs.size- %s' % jobs.qsize())
            #    for thread in workers_t:
            #thread.join()

    def __iter2__(self):
        """
        The function that defines a corpus.
        Iterating over the corpus must yield a document.
        """
        from Queue import Queue
        import threading

        jobs = Queue(maxsize=100 * self.workers)

        def worker_extract():
            while True:
                fname = self.file_queue.get()
                if fname is None:  # data finished, exit
                    break
                with closing(gen_open(fname)) as f:
                    soup = BeautifulSoup('<docs>'+f.read()+'</docs>', 'xml')
                    docs = soup.find_all(self.doctag)
                    for dtag in docs:
                        retdoc = Document()
                        for child in dtag.children:
                            if isinstance(child, Tag):
                                retdoc[child.name] = child.text
                        retdoc.cache_sentences()  # to make it faster, hopefully
                        self.length += 1
                        jobs.put(retdoc)

        workers_t = [threading.Thread(target=worker_extract) for _ in xrange(self.workers)]
        for thread in workers_t:
            thread.daemon = True  # make interrupting the process with ctrl+c easier
            thread.start()

        num = 0
        while True:
            try:
                doc = jobs.get(timeout=5)
                #num += 1
                yield doc
                #if num % 50 == 0:
                #    print 'jobs size:', jobs.qsize()
            except Exception as e:
                print(e.message)
                break

        print('finished extracting documents, with jobs.size- %s' % jobs.qsize())
            #    for thread in workers_t:
            #thread.join()

    def __iter1__(self):

        for fname in self.collection_spec_list:
            with closing(gen_open(fname)) as f:
                soup = BeautifulSoup('<docs>'+f.read()+'</docs>', 'xml')
                docs = soup.find_all(self.doctag)
                for dtag in docs:
                    retdoc = Document()
                    for child in dtag.children:
                        if isinstance(child, Tag):
                            retdoc[child.name] = child.text
                    self.length += 1
                    yield retdoc

    def _toDocument(self, strdoc):
        soup = BeautifulSoup(strdoc, 'xml')
        doctag = soup.find(self.doctag)
        doc = Document()
        for child in doctag.children:
            doc[child.name] = child.text
        return doc
                

    @property
    def length(self):
        return self.length

    def __len__(self):
        return self.length # will throw if corpus not initialized


class Disk125Sentence(object):
    """
    this is only used for word2vec in gensim.

    """
    """
    """
    def __init__(self, fname, cache=0, save_file=None, workers=2):
        """
        cache: 0 in-memory cache the sentences themselves
               1 in-memory, but store the compressed sentences in file-like object in memory
               2 or else, do nothing
        """
        self.fname = fname
        self.corpus = TagCorpus(self.fname, workers=workers)
        self._save = False
        self.cache = cache
        #if save_file:
        #    self._save = True
        #    self.file_writer = gen_open('disk1_5.txt', mode='wb')
        if self.cache == 0:
            self.cache_list = []
        elif self.cache == 1:
            self.strf = StringIO()
            self.file_writer = gzip.GzipFile(filename='test', mode='wb', fileobj=self.strf)
        elif self.cache == 2:
            self.path = save_file if save_file else 'disk1_5.txt'
            self.file_writer = gen_open(self.path, mode='wb')

    def __iter__(self):
        try:
            if self.cache == 0 and self._save:
                for sts in self.cache_list:
                    yield sts
            elif self.cache == 1 and self._save:
                self.strf.seek(0, 0)
                greader = gzip.GzipFile(filename='test', mode='rb', fileobj=self.strf)
                with closing(greader):
                    for line in greader:
                        yield line.split()
            elif self.cache == 2 and self._save:
                greader = gen_open(self.path, mode='rb')
                with closing(greader):
                    for line in greader:
                        yield line.split()
            else:
                self._save = True
                for doc in self.corpus:
                    for pos, sentence in enumerate(doc.to_sentences()):
                        if True:
                            ts = analyzer.tokenStream("dummy", StringReader(str(sentence)))
                            #offsetAtt = ts.addAttribute(OffsetAttribute.class_)
                            termAtt = ts.addAttribute(CharTermAttribute.class_)
                            ts.reset() ##Resets this stream to the beginning. (Required
                            buf = []
                            while ts.incrementToken():
                                buf.append(to_utf8(termAtt.toString()))
                        else:
                            buf = [to_utf8(word.lower().strip()) for word in sentence.split() if word.isalpha()]
                        if self.cache == 0:
                            self.cache_list.append(buf)
                        elif self.cache == 1 or self.cache == 2:
                            self.file_writer.write(' '.join(buf) + '\n')
                        yield buf
                self.file_writer.close()
        except Exception as inst:
            print('error in Disk125', type(inst))
        finally:
            if self._save:
                pass


class Disk125Sentence1(object):
    """
    this is only used for word2vec in gensim.

    """
    def __init__(self, fname):
        """Simple format: one sentence = one line; words already preprocessed and separated by whitespace."""
        self.fname = fname
        self.corpus = TagCorpus(self.fname)

    def __iter__(self):
        try:
            for doc in self.corpus:
                buf = []
                for pos, sentence in enumerate(doc.to_sentences()):
                    tlst = [word.lower().strip() for word in sentence.split() if word.isalpha()]
                    if len(buf) + len(tlst) > 1000:
                        buf.extend(tlst)
                        yield buf
                        buf = []
                    else:
                        buf.extend(tlst)
                #if buf:
                #    yield buf
        except Exception as inst:
            print('error in Disk125', type(inst))



#path = 'collection.spec'
#corpus = TagCorpus(collection_spec=path)
#
#for doc in corpus:
#    for pos, sentence in enumerate(doc.to_sentences()):
#        print pos, sentence
#        if pos > 10:
#            import sys
#            sys.exit(0)
#
#html_doc = """<DOC>
#<DOCNO> AP890101-0001 </DOCNO>
#<FILEID>AP-NR-01-01-89 2358EST</FILEID>
#<FIRST>r a PM-APArts:60sMovies     01-01 1073</FIRST>
#<SECOND>PM-AP Arts: 60s Movies,1100</SECOND>
#<HEAD>You Don't Need a Weatherman To Know '60s Films Are Here</HEAD>
#<BYLINE>By HILLEL ITALIE</BYLINE>
#<BYLINE>Associated Press Writer</BYLINE>
#<DATELINE>NEW YORK (AP) </DATELINE>
#<TEXT>
#   The celluloid torch has been passed to a new
#generation: filmmakers who grew up in the 1960s.
#   ``Platoon,'' ``Running on Empty,'' ``1969'' and ``Mississippi
#Burning'' are among the movies released in the past two years from
#writers and directors who brought their own experiences of that
#turbulent decade to the screen.
#</TEXT>
#</DOC>
#<DOC>
#<DOCNO> AP890101-0001 </DOCNO>
#<FILEID>AP-NR-01-01-89 2358EST</FILEID>
#<FIRST>r a PM-APArts:60sMovies     01-01 1073</FIRST>
#<SECOND>PM-AP Arts: 60s Movies,1100</SECOND>
#<HEAD>You Don't Need a Weatherman To Know '60s Films Are Here</HEAD>
#<BYLINE>By HILLEL ITALIE</BYLINE>
#<BYLINE>Associated Press Writer</BYLINE>
#<DATELINE>NEW YORK (AP) </DATELINE>
#<TEXT>
#   The celluloid torch has been passed to a new
#generation: filmmakers who grew up in the 1960s.
#   ``Platoon,'' ``Running on Empty,'' ``1969'' and ``Mississippi
#Burning'' are among the movies released in the past two years from
#writers and directors who brought their own experiences of that
#turbulent decade to the screen.
#</TEXT>
#</DOC>
#"""

from bs4 import BeautifulSoup
from bs4.element import Tag


#import StringIO
#fst = StringIO.StringIO(html_doc)
#with closing(fst) as f:
#    soup = BeautifulSoup('<docs>'+f.read()+'</docs>', 'xml')
#    docs = soup.find_all('DOC')
#    for doctag in docs:
#        retdoc = Document()
#        for child in doctag.children:
#            if isinstance(child, Tag):
#                retdoc[child.name] = child.text
#        print retdoc

#with closing(fst) as f:
#    strdoc, buf = None, []
#    for line_no, line in enumerate(f):
#
#        if buf and line.startswith('<DOC>'):
#            print buf
#            print _toDocument(''.join(buf))
#            del buf[:]
#            buf.append(line)
#        else:
#            print 'appending,', line
#            buf.append(line)




#import time
#t0 = time.time()
#from bs4 import BeautifulSoup
#from bs4.element import Tag
#soup = BeautifulSoup('<docs>'+html_doc+'</docs>', 'xml', markupMassage=False)

#for i in soup.contents[0].contents:
#    if isinstance(i, Tag):
#        print i.name
#print(soup.prettify())
#
#head = soup.find_all('DOC')
#
#for doc in head:
#    for child in doc.children:
#        print(child)
#
#for doc in head:
#    document = Document(docno=doc.docno.string.strip(),
#                        head=doc.find('HEAD').string,
#                        text=doc.find('text').string,
#                        )
#    print document