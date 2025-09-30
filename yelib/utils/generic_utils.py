# coding: utf-8
try:
    import cPickle as pickle
except ImportError:
    import pickle
import collections
import hashlib
import time
import functools
from contextlib import contextmanager, closing
import os
import io
import gzip
from bz2 import BZ2File
import zlib
import datetime

from logger_utils import setup_logger_loguru as setup_logger

__author__ = "zheng"

logger = setup_logger("debug_only").bind(logger_name="debug_only")


def log_performance(interval=0.1):
    """
    A decorator to measure the execution time of a function.
    automatically determine async or sync function
    
    Parameters
    ----------
    interval : float
        The minimum execution time interval to log. Defaults to 0.1.

    Returns
    -------
    function
        The decorated function.

    """
    def decorator(func):
        import asyncio

        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            async def wrapper(*args, **kwargs):
                start_time = time.time()
                result = await func(*args, **kwargs)
                end_time = time.time()
                if end_time - start_time > interval:
                    logger.info(
                        f"{func.__name__} 执行时间: {end_time - start_time:.3f}秒"
                    )
                return result

        else:

            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                if end_time - start_time > interval:
                    logger.info(
                        f"{func.__name__} 执行时间: {end_time - start_time:.3f}秒"
                    )
                return result

        return wrapper

    return decorator


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
                raise ValueError("Expected a singleton, got {}".format(arg))
            return list(arg)
    else:
        return arg


def timeit(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        start_time = time.time()
        ret_values = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(
            "function [{}] finished in {} ms".format(
                func.__name__, int(elapsed_time * 1000)
            )
        )
        return ret_values

    return new_func


@contextmanager
def timeit_context(name, exit_once_finished=False):
    start_time = time.time()
    yield
    elapsed_time = time.time() - start_time
    print("[{}] finished in {} ms".format(name, int(elapsed_time * 1000)))
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


def md5digest(data):
    md5_gen = hashlib.md5()
    md5_gen.update(data)
    return md5_gen.hexdigest()


def md5hash(my_string):
    m = hashlib.md5()
    m.update(my_string.encode("utf-8"))
    return m.hexdigest()


class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def gzip_pickle_dump(fname, obj, compresslevel=9):
    pickle.dump(
        obj=obj, file=gzip.open(fname, "wb", compresslevel=compresslevel), protocol=2
    )


def gzip_unpickle(fname):
    return pickle.load(gzip.open(fname, "rb"))


def text_compress(text, level=9):
    return zlib.compress(text, level)


def text_decompress(text):
    return zlib.decompress(text)


def random_file_name(
    basename="default", suffix=".jpg", date_formatter="%y-%m%d_%H%M%S", groups=1
):
    """
    :param basename:
    :param suffix:
    :param date_formatter:
    :param groups 生成成group，顺号的文件名，便于比较。
    :return:
    """
    name = datetime.datetime.now().strftime(date_formatter)
    filenames = ["_".join([basename, name, str(i)]) + suffix for i in range(groups)]

    return filenames[0] if groups == 1 else filenames


FLATTEN_TUPLE = "_FLATTEN_TUPLE"


def flatten_dict(d, parent_key="", sep=".") -> dict:
    """
    Flatten a nested dict.

        >>> flatten_dict({'a': 1, 'c': {'a': 2, 'b': {'x': 5, 'y' : 10}}, 'd': [1, 2, 3]})
        >>> {'a': 1, 'c.a': 2, 'c.b.x': 5, 'd': [1, 2, 3], 'c.b.y': 10}

        >>> flatten_dict({'a': 1, 'c': {'a': 2, 'b': {'x': 5, 'y' : 10}}, 'd': [1, 2, 3]}, sep=FLATTEN_TUPLE)
        >>> {'a': 1, ('c','a'): 2, ('c','b','x'): 5, 'd': [1, 2, 3], ('c','b','y'): 10}

    Args:
        d (dict): the dict waiting for flatting
        parent_key (str, optional): the parent key, will be a prefix in new key. Defaults to "".
        sep (str, optional): the separator for string connecting. FLATTEN_TUPLE for tuple connecting.

    Returns:
        dict: flatten dict
    """
    items = []
    for k, v in d.items():
        if sep == FLATTEN_TUPLE:
            new_key = (parent_key, k) if parent_key else k
        else:
            new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


if __name__ == "__main__":
    import random

    cjb = []
    for i in range(5):
        name = input("name:")  # 姓名
        cj = random.randint(50, 100)  # 随机生成50——100之间的整数作为成绩
        cjb.append([name, cj])
    print(cjb)

    gzip_pickle_dump("output.pklzip", cjb)
    print(gzip_unpickle("output.pklzip"))

    # 将成绩表中的数据保存到cjb.txt文件中
    with open("cjb.txt", "wb") as f:
        pickle.dump(cjb, f)
