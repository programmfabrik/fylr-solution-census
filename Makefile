PLUGIN_NAME ?= solution-census
REPO_NAME ?= easydb-solution-census-plugin

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
	rm -rf src/server/*.pyc $(REPO_NAME)

wipe: wipe-base

zip: build
	mkdir -p $(REPO_NAME)/src
	cp -r build $(REPO_NAME)/
	cp -r build-info.json $(REPO_NAME)/
	cp -r src/server $(REPO_NAME)/src/
	cp -r l10n $(REPO_NAME)/
	cp -r easydb-library $(REPO_NAME)/
	cp -r manifest.yml $(REPO_NAME)/
	zip -r $(PLUGIN_NAME).zip $(REPO_NAME)
	make clean