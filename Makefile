PLUGIN_NAME = solution-census

L10N_FILES = l10n/$(PLUGIN_NAME).csv
L10N_GOOGLE_KEY = 1_SRL--Xf9bAX87amqKbJP-AiZixA5tzt-lVnVXDP_50
L10N_GOOGLE_GID = 0


INSTALL_FILES = \
	$(WEB)/l10n/cultures.json \
	$(WEB)/l10n/de-DE.json \
	$(WEB)/l10n/en-US.json \
	src/server/set_image_name.py \
	$(JS) \
	manifest.yml


COFFEE_FILES = src/webfrontend/CustomBaseConfig.coffee


all: google_csv build

include easydb-library/tools/base-plugins.make

build: code $(L10N) buildinfojson

code: $(JS)

clean: clean-base
	rm -f src/server/*.pyc

wipe: wipe-base
