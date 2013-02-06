from lettuce import *

# parse from the resource whose name is `resource_name'
@step(u'And that has a resource called "([^"]*)"')
def thatHasAResource(step, resource_name):
    world.structure = world.structure['Resources'][resource_name]


# parse from the mapping whose name is `mapping_name'
@step(u'And that has a mapping called "([^"]*)"')
def thatHasAMapping(step, mapping_name):
    world.structure = world.structure['Mappings'][mapping_name]


# parse from the parameters whose name is `parameter_name'
@step(u'And that has a parameter called "([^"]*)"')
def thatHasAParameter(step, parameter_name):
    world.structure = world.structure['Parameters'][parameter_name]


# parse from the output whose name is `output_name'
@step(u'And that has a output called "([^"]*)"')
def thatHasAOutput(step, output_name):
    world.structure = world.structure['Outputs'][output_name]


# parse from the property whose name is `property_name'
@step(u'And that has a property called "([^"]*)"')
def propertyCheck(step, property_name):
    world.structure = world.structure['Properties'][property_name]


# parse from the key whose name is `key_name'
@step(u'And that has a key called "([^"]*)"')
def thatHasAKey(step, key_name):
    world.structure = world.structure[key_name]


# assert the type is equal to `value', e.g. for a parameter
@step(u'Then its type is "([^"]*)"')
def typeCheck(step, value):
    assert world.structure['Type'] == value


# assert the value of a key is equal to `value'
@step(u'Then the value for that key is "([^"]*)"')
def valueForKeyIs(step, value):
    # if `world.structure' is a boolean, convert it to a lowercase, unicode string and perform the assertion
    if isinstance(world.structure, bool):
        assert unicode(world.structure).lower() == value
    # if `world.structure' is an integer, convert it to a unicode string and perform the assertion
    elif isinstance(world.structure, int):
        assert unicode(world.structure) == value
    else:
        # `world.structure' is unicode
        assert world.structure == value


# assert the current `world.structure' is a reference to `value'
@step(u'Then it is a reference to "([^"]*)"')
def isAReferenceTo(step, value):
    assert world.structure == { "Ref" : value }


# assert the default value for a parameter is `value'
@step(u'Then its default is "([^"]*)"')
def itsDefaultIs(step, value):
    assert world.structure['Default'] == value


# assert specified tags for a resource exist
@step(u'Then there is a tag whose key is "([^"]*)" and whose value is "([^"]*)"')
def thenCheckThisTagExists(step, key, value):

    # set the pointer to the Tags element
    tags_from_template = world.structure['Properties']['Tags']

    # set tag_matches variable to False
    tag_matches = False

    # parse tags from the template
    for num, val in enumerate(tags_from_template):
        key_template = tags_from_template[num]['Key']
        value_template = tags_from_template[num]['Value']

        # check if the tag value from the template is actually a reference rather than a value
        value_template_is_reference = False
        if value_template == { "Ref" : value }:
            value_template_is_reference = True

        # scan tags for the resource and exit the loop if a matching key/value pair is found
        if key_template == key \
                and (value_template == value or value_template_is_reference):
            tag_matches = True
            break
    assert tag_matches
