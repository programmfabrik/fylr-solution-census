# config for Google CSV spreadsheet
L10N = l10n/fylr-solution-census.csv
GKEY = 1_SRL--Xf9bAX87amqKbJP-AiZixA5tzt-lVnVXDP_50
GID_LOCA = 0
GOOGLE_URL = https://docs.google.com/spreadsheets/u/1/d/$(GKEY)/export?format=csv&gid=

# config to build javascript
JS =
COFFEE_FILES =
PLUGIN_NAME = fylr-solution-census
BUILD_DIR = build

ZIP_NAME ?= "${PLUGIN_NAME}.zip"

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

google-csv: ## get loca CSV from google
	curl --silent -L -o - "$(GOOGLE_URL)$(GID_LOCA)" | tr -d "\r" > $(L10N)

all: google-csv build ## pull CSV & build

build: clean code ## build all (creates build folder)
	mkdir -p $(BUILD_DIR)/$(PLUGIN_NAME)
	cp manifest.master.yml $(BUILD_DIR)/$(PLUGIN_NAME)/manifest.yml
	#cp -r src/server l10n $(BUILD_DIR)/$(PLUGIN_NAME)
	#mkdir -p $(BUILD_DIR)/$(PLUGIN_NAME)/webfrontend
	#cp -r $(JS) $(BUILD_DIR)/$(PLUGIN_NAME)/webfrontend

code: $(JS) ## build Coffeescript code

clean: ## clean build files
	rm -f src/server/*.pyc
	rm -f src/webfrontend/*.coffee.js
	rm -f $(JS)
	rm -rf $(BUILD_DIR)

zip: build ## build zip file for publishing
	cd $(BUILD_DIR) && zip ${ZIP_NAME} -r $(PLUGIN_NAME)

${JS}: $(subst .coffee,.coffee.js,${COFFEE_FILES})
	mkdir -p $(dir $@)
	cat $^ > $@

%.coffee.js: %.coffee
	coffee -b -p --compile "$^" > "$@" || ( rm -f "$@" ; false )