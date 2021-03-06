from contextlib import contextmanager
from copy import deepcopy
from json import dumps as j_dump
from json import loads as j_load

from yaml import dump as y_dump
from yaml import load as y_load
from yaml.parser import ParserError
from yaml.scanner import ScannerError


def merge_dicts(first, second):
    '''
    Merge nested dictionaries deeply

    :param first: Source dictionary
    :param second: Dictionary to merge into ``first``
    :return dict: merged dictionaries
    '''
    if not isinstance(second, dict):
        return second
    res = deepcopy(first)
    if isinstance(res, dict):
        for key in second.keys():
            res[key] = (
                merge_dicts(res[key], second[key]) if
                res.get(key) and isinstance(res[key], dict) else
                deepcopy(second[key])
            )
    return res


@contextmanager
def load_struct(content, fallback=None, as_yaml=False,):
    '''
    Contextmanager to unpickle either *json* or *yaml* from a string

    :param content: string to unpickle
    :param fallback: data to return in case of unpickle failure
    :param as_yaml: read as *yaml* instead of *json*
    :yield: unpickled ``content``
    '''
    try:
        yield (
            y_load(content) if as_yaml else j_load(content)
        ) if isinstance(content, str) else fallback
    except (ValueError, ScannerError, ParserError):
        yield fallback


@contextmanager
def dump_struct(content, as_yaml=False):
    '''
    Contextmanager to pickle either *json* or *yaml* into a string

    :param content: data to pickle
    :param as_yaml: output as *yaml* instead of *json*
    :yield str: pickled ``content``
    '''
    try:
        yield y_dump(
            content, indent=4, default_flow_style=False
        ) if as_yaml else j_dump(
            content, indent=2, sort_keys=True
        )
    except TypeError:
        yield None
