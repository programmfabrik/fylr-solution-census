PLUGIN_NAME = fylr-solution-census-plugin

L10N_FILES = l10n/$(PLUGIN_NAME).csv
L10N_GOOGLE_KEY = 1_SRL--Xf9bAX87amqKbJP-AiZixA5tzt-lVnVXDP_50
L10N_GOOGLE_GID = 0


INSTALL_FILES = \
	$(WEB)/l10n/cultures.json \
	$(WEB)/l10n/de-DE.json \
	$(WEB)/l10n/en-US.json \
	manifest.yml

all: google_csv

include easydb-library/tools/base-plugins.make

build: $(L10N) buildinfojson

clean: clean-base

wipe: wipe-base
