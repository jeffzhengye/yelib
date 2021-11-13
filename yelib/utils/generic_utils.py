# coding: utf-8
try:
    import cPickle as pickle
except:
    import pickle
import time
import functools
from contextlib import contextmanager
import os
import io
import gzip
from bz2 import BZ2File
from contextlib import closing
import zlib
import md5
import datetime

__author__ = 'zheng'


def unpack(arg, singleton=False):
    """Unpack variables from a list or tuple.

    Parameters
    ----------
    arg : object
        Either a list or tuple, or any other Python object. If passed a
        list or tuple of length one, the only element of that list will
        be returned. If passed a tuple of length greater than one, it
        will be cast to a list before returning. Any other variable
        will be returned as is.
    singleton : bool
        If ``True``, `arg` is expected to be a singleton (a list or tuple
        with exactly one element) and an exception is raised if this is not
        the case. ``False`` by default.

    Returns
    -------
    object
        A list of length greater than one, or any other Python object
        except tuple.

    """
    if isinstance(arg, (list, tuple)):
        if len(arg) == 1:
            return arg[0]
        else:
            if singleton:
                raise ValueError("Expected a singleton, got {}".
                                 format(arg))
            return list(arg)
    else:
        return arg


def timeit(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print('function [{}] finished in {} ms'.format(
            func.__name__, int(elapsed_time * 1000)))

    return new_func


@contextmanager
def timeit_context(name, exit_once_finished=False):
    start_time = time.time()
    yield
    elapsed_time = time.time() - start_time
    print('[{}] finished in {} ms'.format(name, int(elapsed_time * 1000)))
    if exit_once_finished:
        import sys
        sys.exit(1)


def update_dict(input_dict, update_dict):
    def _update(dict1, dict2):
        for key, value in dict2.iteritems():
            if key in dict1:
                if type(value) == dict:
                    _update(dict1[key], value)
                else:
                    dict1[key] = value
            else:
                dict1[key] = value
    _update(input_dict, update_dict)


def md5digest(str):
    md5_gen = md5.new()
    md5_gen.update(str)
    return md5_gen.hexdigest()


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def gzip_pickle_dump(fname, obj, compresslevel=9):
    pickle.dump(obj=obj, file=gzip.open(fname, "wb", compresslevel=compresslevel), protocol=2)


def gzip_unpickle(fname):
    return pickle.load(gzip.open(fname, "rb"))


def text_compress(text, level=9):
    return zlib.compress(text, level)


def text_decompress(text):
    return zlib.decompress(text)


def random_file_name(basename='default', suffix='.jpg', date_formatter="%y-%m%d_%H%M%S"):
    """
    :param basename:
    :param suffix:
    :param date_formatter:
    :return:
    """
    name = datetime.datetime.now().strftime(date_formatter)
    filename = "_".join([basename, name]) + suffix
    return filename
