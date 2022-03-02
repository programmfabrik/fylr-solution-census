# easydb-solution-census-plugin

Submodule for the `core`-plugin of the `census` solution.

## Features:

Before object(s) of the objecttype `cs_name` are saved, the plugin checks if the field `name` is empty. In this case, it is filled with a sequential number and the prefix `HU`. This is used to auto generate unique names for batches of new `cs_image` objects.

## related tickets:

- based on https://tickets.programmfabrik.de/ticket/59959
