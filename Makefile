PLUGIN_NAME = set_image_name
INSTALL_FILES = \
	src/server/set_image_name.py \
	manifest.yml


all: build

include ../easydb-library/tools/base-plugins.make

build: code

code: $(L10N)

clean: clean-base

wipe: wipe-base
