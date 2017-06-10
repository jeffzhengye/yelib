import os
import io
from bz2 import BZ2File
from contextlib import closing
import gzip


def gen_open(f, mode='rb'):
    if isinstance(f, int):  # file descriptor
        return io.open(f, mode, closefd=False)
    elif not isinstance(f, basestring):
        raise TypeError("expected {str, int, file-like}, got %s" % type(f))
    _, ext = os.path.splitext(f)
    if ext == ".gz":
        return gzip.open(f, mode)
    elif ext == ".bz2":
        return BZ2File(f, mode)
    else:
        return open(f, mode)


def file2str_list(filename, to_lower=False, encoding='utf-8'):
    """return a list from a file
        support normal compressed files
    """
    with closing(gen_open(filename)) as f:
        lines = f.read().decode(encoding).splitlines()
        if to_lower:
            lines = [x.strip().lower() for x in lines]
        return lines


def list2file(string_list, output, encoding='utf-8'):
    import codecs
    with codecs.open(output, "w", encoding) as f:
        f.write('\n'.join(string_list))
