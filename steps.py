import json
import boto

from lettuce import *

@step(u'Given I have a template called "([^"]*)"')
def loadTemplate(step, template_name):
    f = open(template_name)
    world.template_raw = f.read()
    f.close()
    world.template = json.loads(world.template_raw)
    world.structure = world.template


# Validation
@step(u'Then it is valid CloudFormation')
def validCloudFormation(step):
    cloudformation = boto.connect_cloudformation()
    try:
        cloudformation.validate_template(template_body=world.template_raw)
    except boto.exception.BotoServerError:
        raise AssertionError('The template is not valid CloudFormation!')


# CFN Top Level Stuff
@step(u'And that has a resource called "([^"]*)"')
def thatHasAResource(step, resource_name):
    world.structure = world.structure['Resources'][resource_name]

@step(u'And that has a mapping called "([^"]*)"')
def thatHasAMapping(step, mapping_name):
    world.structure = world.structure['Mappings'][mapping_name]

@step(u'And that has a parameter called "([^"]*)"')
def thatHasAParameter(step, parameter_name):
    world.structure = world.structure['Parameters'][parameter_name]

@step(u'And that has a output called "([^"]*)"')
def thatHasAOutput(step, output_name):
    world.structure = world.structure['Outputs'][output_name]


# Generic stuff
@step(u'Then its type is "([^"]*)"')
def typeCheck(step, value):
    assert world.structure['Type'] == value

@step(u'And that has a property called "([^"]*)"')
def propertyCheck(step, a_property):
    world.structure = world.structure['Properties'][a_property]

@step(u'And that has a key called "([^"]*)"')
def thatHasAKey(step, key_name):
    world.structure = world.structure[key_name]

@step(u'Then the value for that key is "([^"]*)"')
def valueForKeyIs(step, value):
    if world.structure in [True, False]:
        assert unicode(world.structure).lower() == value
    else:
        assert world.structure == value

@step(u'Then it is a reference to "([^"]*)"')
def isAReferenceTo(step, value):
    assert world.structure == {'Ref': value}


# Parameters
@step(u'Then its default is "([^"]*)"')
def itsDefaultIs(step, value):
    assert world.structure['Default'] == value
