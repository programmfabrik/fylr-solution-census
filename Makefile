PLUGIN_NAME = fylr-solution-census-plugin

L10N = l10n/$(PLUGIN_NAME).csv
GKEY = 1_SRL--Xf9bAX87amqKbJP-AiZixA5tzt-lVnVXDP_50
GID_LOCA = 0
GOOGLE_URL = https://docs.google.com/spreadsheets/u/1/d/$(GKEY)/export?format=csv&gid=

INSTALL_FILES = \
	$(WEB)/l10n/cultures.json \
	$(WEB)/l10n/de-DE.json \
	$(WEB)/l10n/en-US.json \
	manifest.yml

google-csv: ## get loca CSV from google
	curl --silent -L -o - "$(GOOGLE_URL)$(GID_LOCA)" | tr -d "\r" > $(L10N)

all: google-csv

build: $(L10N) buildinfojson

clean: clean-base

wipe: wipe-base
