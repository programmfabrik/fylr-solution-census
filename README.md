# easydb-solution-census-plugin

Submodule for the `core`-plugin of the `census` solution.

## Features:

Before object(s) of the objecttype `cs_name` are saved, the plugin checks if the field `name` is empty. In this case, it is filled with a sequential number and the prefix `HU`. This is used to auto generate unique names for batches of new `cs_image` objects.

> This plugin needs an objecttype to store sequential numbers!

This means, in the datamodel there must be an additional objecttype which stores the latest used unique sequential number.

The plugin has the following requirements:

* objecttype name: `sequence`
* text field: `reference`
    * this field stores a unique identifier so the plugin knows which object to use
    * `NOT NULL`
    * `UNIQUE`
* integer field: `number`
    * this field stores the latest used sequential number
    * `NOT NULL`


The plugin uses the combination of `reference` and `number` to get the latest number to use as an offset, and the object ID and version if an object with the plugin reference exists.

The plugin determines how many numbers of the sequence it will use, and update the sequence object (or create a new one if the sequence is used for the first time). If another plugin instance has updated the sequence already, the versions will not match, and the plugin tries to repeat the process again. The actual objects are only updated after the sequence update was successful.


The reference for this plugin is `census.core.set_image_name`. The plugin will create an object with this reference if it does not exist. The sequential number will be increased after each insert of `cs_image` image object(s). To update the next sequential number, an object with this reference can be created or updated and the number can be set.

> Make sure to not use a lower number that might already have been used for `cs_image.name` to avoid any unique constraint violations.

## related tickets:

- based on https://tickets.programmfabrik.de/ticket/59959
