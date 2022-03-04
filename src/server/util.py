# encoding: utf-8

from datetime import datetime
import json
import sys
import traceback
import requests


# helper functions

def write_tmp_file(name, lines, new_file=False, dir='/tmp/'):
    if not isinstance(lines, list):
        lines = [lines]

    lines = [str(datetime.now()), ''] + lines

    if not dir.endswith('/'):
        dir += '/'
    with open(dir + name, 'w' if new_file else 'a') as tmp:
        tmp.writelines(map(lambda l: l + '\n', lines))


def handle_exceptions(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            exc_info = sys.exc_info()
            stack = traceback.extract_stack()
            tb = traceback.extract_tb(exc_info[2])
            full_tb = stack[:-1] + tb
            exc_line = traceback.format_exception_only(*exc_info[:2])

            trace = [str(repr(e))] + traceback.format_list(full_tb) + exc_line

            return_error_response('\n'.join(trace))

    return func_wrapper


def get_json_value(js, path, expected=False):
    current = js
    path_parts = path.split('.')
    for path_part in path_parts:
        if not isinstance(current, dict) or path_part not in current:
            if expected:
                raise Exception('expected: ' + path_part)
            else:
                return None
        current = current[path_part]
    return current


def dumpjs(js, indent=4):
    return json.dumps(js, indent=indent)


# plugin response functions


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

# fylr api functions


def fylr_api_headers(access_token):
    return {
        'authorization': 'Bearer ' + access_token,
    }


def get_from_api(api_url, path, access_token):
    resp = requests.get(
        api_url + '/' + path,
        headers=fylr_api_headers(access_token))

    return resp.text, resp.status_code


def post_to_api(api_url, path, access_token, payload=None):
    resp = requests.post(
        api_url + '/' + path,
        headers=fylr_api_headers(access_token),
        data=payload)

    return resp.text, resp.status_code


class FylrSequence(object):
    OT_SEQ = 'sequence'
    OT_SEQ_REF = 'reference'
    OT_SEQ_NUM = 'number'

    current_number = 1
    obj_id = None
    version = 1

    def __init__(self, api_url, ref, access_token) -> None:
        self.api_url = api_url
        while self.api_url.endswith('/'):
            self.api_url = self.api_url[:-1]
        self.ref = ref
        self.access_token = access_token

    @handle_exceptions
    def get_from_api(self, path):
        return get_from_api(self.api_url, path, self.access_token)

    @handle_exceptions
    def post_to_api(self, path, payload=None):
        return post_to_api(self.api_url, path, self.access_token, payload)

    @handle_exceptions
    def get_next_number(self) -> int:
        path = 'db/' + self.OT_SEQ + '/_all_fields/list'
        api_resp, statuscode = self.get_from_api(path)

        if statuscode != 200:
            raise Exception('invalid response: ' +
                            str(statuscode) + ' - ' + api_resp)

        if len(api_resp) < 1:
            raise Exception('invalid response: expected non-empty body')

        objects = json.loads(api_resp)
        if not isinstance(objects, list):
            raise Exception('invalid response: expected array - ' + api_resp)

        for obj in objects:
            if get_json_value(obj, self.OT_SEQ + '.' + self.OT_SEQ_REF) != self.ref:
                continue

            # get the last used number of the sequence
            n = get_json_value(
                obj, self.OT_SEQ + '.' + self.OT_SEQ_NUM)
            if n is None or n < 1:
                n = 1

            # update offset, object id and version
            self.current_number = n
            self.obj_id = get_json_value(obj, self.OT_SEQ + '._id')
            self.version = get_json_value(obj, self.OT_SEQ + '._version')

            break

        # return the next free number of the sequence
        return self.current_number

    @handle_exceptions
    def update(self, new_number: int):

        if new_number <= self.current_number:
            return False, None

        new_obj = {
            '_objecttype': self.OT_SEQ,
            '_mask': '_all_fields',
            self.OT_SEQ: {
                '_id': self.obj_id,
                '_version': 1 if self.obj_id is None else self.version + 1,
                self.OT_SEQ_NUM: new_number,
                self.OT_SEQ_REF: self.ref
            }
        }

        resp, statuscode = post_to_api(
            self.api_url,
            'db/' + self.OT_SEQ,
            self.access_token,
            dumpjs([new_obj])
        )

        # determine if the caller should try to repeate a failed update or give up

        if statuscode == 200:
            # everything ok
            self.version += 1
            return True, None

        elif statuscode >= 400 and statuscode < 500:
            # some api error, maybe wrong version
            # => caller should repeat the process, and get the new current sequence number
            return False, None

        else:
            # something went wrong, caller should not try to repeat updating the sequence
            error = {
                'url': self.api_url + '/db/' + self.OT_SEQ,
                'statuscode': statuscode,
            }
            error_resp = None
            try:
                error_resp = json.loads(resp)
            except:
                error_resp = resp
            error['response'] = error_resp

            return False, error
