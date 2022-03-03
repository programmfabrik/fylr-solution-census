# encoding: utf-8


import sys

import util
import json

OBJECTTYPE = 'cs_image'
NAME_FIELD = 'name'

PLUGIN_REF = 'census.core.set_image_name'


NAME_PREFIX = 'HU'


@util.handle_exceptions
def main():

    orig_data = json.loads(sys.stdin.read())

    # get the server url
    api_url = util.get_json_value(orig_data, 'info.api_url')
    if api_url is None:
        util.return_error_response('info.api_url missing!')
    api_url += '/api/v1'

    # get a session token
    access_token = util.get_json_value(
        orig_data, 'info.api_user_access_token')
    # # xxx
    # access_token= 'Xkq_tiukcdy_4zJzo4EipNKatPGPpe17estLEMdLJQk.HCpv3YtUWdMRfdlXn4a-Oi7_I2ny-akSw9uenMaLHKY'
    if access_token is None:
        util.return_error_response('info.api_user_access_token missing!')

    # iterate over objects and check if the name must be set
    objects = util.get_json_value(orig_data, 'objects')
    if not isinstance(objects, list):
        util.return_response(orig_data)

    # collect indices of objects that need to be updated
    # determine the new offset of the sequence
    indices_to_update = set()
    for i in range(len(objects)):
        obj = objects[i]

        if not isinstance(obj, dict):
            continue

        objecttype = util.get_json_value(obj, '_objecttype')
        if objecttype != OBJECTTYPE:
            # another objecttype was inserted, nothing to do here
            continue

        # skip if not INSERT
        version = util.get_json_value(obj, OBJECTTYPE + '._version')
        if version != 1:
            # object was updated, nothing to do here
            continue

        name = util.get_json_value(
            obj,
            '%s.%s' % (OBJECTTYPE, NAME_FIELD))
        if name not in [None, '']:
            # name is already set, nothing to do here
            continue

        indices_to_update.add(i)

    if len(indices_to_update) < 1:
        # no updates in objects necessary, just return the original data
        util.return_response(orig_data)

    # if any names need to be update, get the next offset in the sequence
    seq = util.FylrSequence(api_url, PLUGIN_REF, access_token)
    offset = seq.get_next_number()

    util.write_tmp_file('set_image_name.log', [
        'offset: ' + str(offset)
    ], new_file=True)

    # update the new sequence to check if it has not been changed by another instance, else xxxrepeatxxx
    update_objects = False
    # todo

    # todo if the new sequence was updated, update the actual objects

    if update_objects:
        data = []
        for i in range(len(objects)):
            obj = objects[i]

            if i not in indices_to_update:
                # object is not affected, just copy it into the response
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
            name = '%s%06d' % (NAME_PREFIX, offset)
            offset += 1

            obj[OBJECTTYPE][NAME_FIELD] = name

            data.append(obj)

        response = orig_data
        response['objects'] = data

        util.return_response(response)


if __name__ == '__main__':
    main()
