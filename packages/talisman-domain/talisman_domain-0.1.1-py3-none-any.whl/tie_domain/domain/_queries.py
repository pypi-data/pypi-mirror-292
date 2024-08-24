common_fields = '''
    id
    name
'''


def build_concept_value_fields(
        list_white_dictionary: bool = True,
        black_list: bool = True
):
    concept_value_fields = f'''
        {common_fields}
        regexp: listWhiteRegexp {{
            regexp
            context_regexp: contextRegexp
            auto_create: autoCreate
        }}
        black_regexp: listBlackRegexp {{
            regexp
            context_regexp: contextRegexp
            auto_create: autoCreate
        }}
        {"black_list: listBlackDictionary"  if black_list else ""}
        {"list_white_dictionary: listWhiteDictionary" if list_white_dictionary else ""}
        pretrained_nerc_models: pretrainedNERCModels
    '''
    return concept_value_fields


def build_concept_types(
        list_names_dictionary: bool = True,
        list_white_dictionary: bool = True,
        black_list: bool = True
):
    concept_types = f'''
    listConceptType: listConceptType {{
        {build_concept_value_fields(list_white_dictionary, black_list)}
        metaType
        {"list_names_dictionary: listNamesDictionary" if list_names_dictionary else ""}
    }}
    '''
    return concept_types


concept_property_value_types = f'''
    listConceptPropertyValueType: listConceptPropertyValueType {{
        {build_concept_value_fields()}
        value_type: valueType
        value_restriction: valueRestriction
    }}
'''

composite_property_value_types = f'''
    listCompositePropertyValueTemplate: listCompositePropertyValueTemplate {{
        {common_fields}
        componentValueTypes {{
            {common_fields}
            valueType {{
                {build_concept_value_fields()}
                value_type: valueType
                value_restriction: valueRestriction
            }}
        }}
    }}
'''

property_link_types = f'''
    {common_fields}
    pretrained_relext_models: pretrainedRelExtModels {{
        source_annotation: sourceAnnotationType
        target_annotation: targetAnnotationType
        invert_direction: invertDirection
        relation_type: relationType
    }}
'''

link_types = f'''
    listConceptPropertyValueType: listConceptLinkType {{
        {property_link_types}
        conceptFromType {{
            id
        }}
        conceptToType {{
            id
        }}
        is_directed: isDirected
    }}
'''

property_types = f'''
    listConceptPropertyValueType: listConceptPropertyType {{
        {property_link_types}
        isIdentifying
        parentConceptType {{
            id
        }}
        parentConceptLinkType {{
            id
        }}
        valueType {{
            ... on ConceptPropertyValueType {{
                id
            }}
            ... on CompositePropertyValueTemplate {{
                id
            }}
        }}
    }}
'''
