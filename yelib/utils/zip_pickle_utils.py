try:
    import cPickle as pickle
except:
    import pickle
import zlib
import gzip

__author__ = 'zheng'


def zlib_dumps(obj):
    return zlib.compress(pickle.dumps(obj, pickle.HIGHEST_PROTOCOL), 9)


def zlib_loads(zstr):
    return pickle.loads(zlib.decompress(zstr))


def gzip_pickle(fname, obj, compresslevel=9):
    pickle.dump(obj=obj, file=gzip.open(fname, "wb", compresslevel=compresslevel), protocol=2)


def gzip_unpickle(fname):
    return pickle.load(gzip.open(fname, "rb"))


def test():
    import numpy
    import os
    tmp_file = "tmp_test.zippkl"
    z = numpy.random.ranf((1000, 2000))
    print (len(z.dumps()))
    print (len(pickle.dumps(z.dumps())))
    print (len(zlib_dumps(z)))

    gzip_pickle(tmp_file, z)
    print (os.path.getsize(tmp_file))

if __name__ == '__main__':
    test()
