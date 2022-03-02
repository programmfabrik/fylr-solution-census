# encoding: utf-8

import json
import sys
import traceback


def print_traceback(e):
    exc_info = sys.exc_info()
    stack = traceback.extract_stack()
    tb = traceback.extract_tb(exc_info[2])
    full_tb = stack[:-1] + tb
    exc_line = traceback.format_exception_only(*exc_info[:2])
    return [
        repr(e),
        traceback.format_list(full_tb) + exc_line
    ]


class SkipDataException(Exception):
    def __init__(self, data, msg):
        Exception()
        self.msg = msg
        self.data = data

    def getMessage(self):
        return self.msg

    def __str__(self):
        return self.getMessage()


class VerboseException(Exception):
    def __init__(self, msg):
        Exception()
        self.msg = msg

    def getMessage(self):
        return self.msg

    def __str__(self):
        return self.getMessage()


def get_json_value(js, path, expected=False):
    current = js
    path_parts = path.split('.')
    for path_part in path_parts:
        if not isinstance(current, dict) or path_part not in current:
            if expected:
                raise VerboseException('expected: {0}'.format(path_part))
            else:
                return None
        current = current[path_part]
    return current


def dumpjs(js, indent=4):
    return json.dumps(js, indent=4)


def stdout(line):
    sys.stdout.write(line)
    sys.stdout.write('\n')


def stderr(line):
    sys.stderr.write(line)
    sys.stderr.write('\n')


def return_response(response):
    stdout(dumpjs(response))
    exit(0)


def return_error_response(error):
    stderr(error)
    exit(1)
