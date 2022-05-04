class CustomBaseConfigCore extends BaseConfigPlugin
    getFieldDefFromParm: (baseConfig, fieldName, def) ->

        getMask = (idTable) ->
            if CUI.util.isString(idTable)
                return false
            return Mask.getMaskByMaskName("_all_fields", idTable)

        switch def.plugin_type
            when "objecttype"
                field = new ez5.ObjecttypeSelector
                    form: label: $$("server.config.name.system.census.core.census-solution.set_image_name.objecttype.label")
                    name: fieldName
                    show_name: true
                    store_value: "fullname"
                    filter: (objecttype) ->
                        mask = getMask(objecttype.table.id())
                        if not mask
                            return false

                        objecttype.addMask(mask)

                        # todo: unique not null text field
                        hasRefField = objecttype.getFields().some((field) -> field instanceof TextColumn)

                        # todo: not null number field
                        hasNumField = objecttype.getFields().some((field) -> field instanceof NumberColumn)

                        return hasRefField and hasNumField

            when "ref_field"
                field = new ez5.FieldSelector
                    form: label: $$("server.config.name.system.census.core.census-solution.set_image_name.ref_field.label")
                    name: fieldName
                    objecttype_data_key: "objecttype"
                    store_value: "fullname"
                    show_name: true
                    filter: (field) ->
                        return field instanceof TextColumn and
                            field not instanceof NestedTable and
                            field not instanceof NumberColumn and
                            field not instanceof LocaTextColumn and
                            not field.isTopLevelField() and
                            not field.insideNested()

            when "num_field"
                field = new ez5.FieldSelector
                    form: label: $$("server.config.name.system.census.core.census-solution.set_image_name.num_field.label")
                    name: fieldName
                    objecttype_data_key: "objecttype"
                    store_value: "fullname"
                    show_name: true
                    filter: (field) =>
                        return field instanceof NumberColumn and
                            not field.isTopLevelField() and
                            not field.insideNested()

        return field

ez5.session_ready =>
    BaseConfig.registerPlugin(new CustomBaseConfigCore())