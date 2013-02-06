import boto
import json

from lettuce import *

# load the template file from disk
# store its JSON structure into `world.template'
# copy `world.template' into `world.structure' for subsequent use
@step(u'Given I have a template called "([^"]*)"')
def loadTemplate(step, template_name):
    f = open(template_name)
    world.template_raw = f.read()
    f.close()
    world.template = json.loads(world.template_raw)
    world.structure = world.template


# connect to the AWS API and validate the template
@step(u'Then it is valid CloudFormation')
def validCloudFormation(step):
    cloudformation = boto.connect_cloudformation()
    try:
        cloudformation.validate_template(template_body=world.template_raw)
    except boto.exception.BotoServerError:
        raise AssertionError('The template is not valid CloudFormation!')
