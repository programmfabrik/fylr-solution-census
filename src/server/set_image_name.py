# encoding: utf-8


import sys
import time
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

    # repeat:
    # 1:    get the next number of the sequence (from an existing object, or 1 if the sequence has not been used yet)
    # 2:    determine the new maximum number of the sequence (depending on how many objects need an update)
    # 3:    try to update the sequence object (protected by object version)
    # 4:    if the sequence was updated, update and return the objects, break loop

    seq = util.FylrSequence(api_url, PLUGIN_REF, access_token)

    do_repeat = True
    repeated = 0
    while do_repeat:
        do_repeat = False

        offset = seq.get_next_number()

        # update the new sequence to check if it has not been changed by another instance
        update_ok, error = seq.update(offset + len(indices_to_update))

        if error is not None:
            # indicator that something went wrong and the plugin should just return an error message
            util.return_error_response(util.dumpjs({
                'error': 'could not update sequence',
                'reason': error
            }))

        if not update_ok:
            # sleep for 1 second and try again to get and update the sequence
            time.sleep(1)

            do_repeat = True
            repeated += 1

            continue

        # sequence was updated, unique sequence values can be used to update objects
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

        # everything ok, update and return the objects, exit program

        response = orig_data
        response['objects'] = data

        util.return_response(response)


if __name__ == '__main__':
    main()
