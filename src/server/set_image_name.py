# encoding: utf-8


import sys
from urllib import response
import util
import json

OBJECTTYPE = 'cs_image'
NAME_FIELD = 'name'

NAME_PREFIX = 'HU'

if __name__ == '__main__':

    try:
        orig_data = json.loads(sys.stdin.read())

        data = []

        # todo: get actual number
        num = 1

        objects = util.get_json_value(orig_data, 'objects')
        if not isinstance(objects, list):
            raise util.SkipDataException(
                orig_data,
                'expect objects in array'
            )

        for i in range(len(objects)):
            obj = objects[i]

            if not isinstance(obj, dict):
                raise util.SkipDataException(
                    orig_data,
                    'object %d is not an object' % i
                )

            objecttype = util.get_json_value(obj, '_objecttype')
            if objecttype != OBJECTTYPE:
                # another objecttype was inserted, nothing to do here
                data.append(obj)
                continue

            # skip if not INSERT
            version = util.get_json_value(obj, OBJECTTYPE + '._version')
            if version != 1:
                # object was updated, nothing to do here
                data.append(obj)
                continue

            name = util.get_json_value(
                obj,
                '%s.%s' % (OBJECTTYPE, NAME_FIELD))
            if name not in [None, '']:
                # name is already set, nothing to do here
                data.append(obj)
                continue

            # replace the empty name with a prefix and a running number
            name = '%s%06d' % (NAME_PREFIX, num)
            num += 1

            obj[OBJECTTYPE][NAME_FIELD] = name

            data.append(obj)

        response = orig_data
        response['objects'] = data

        util.return_response(response)

    except util.SkipDataException as e:
        # will not change the data of the object(s)
        util.return_response(e.data)

    except util.VerboseException as e:
        util.return_error_response(e.getMessage())

    except Exception as e:
        trace = util.print_traceback(e)
        util.return_error_response('\n'.join(trace))
