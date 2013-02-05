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
# if `world.structure' is a Boolean (True or False) convert it to a lowercase string
@step(u'Then the value for that key is "([^"]*)"')
def valueForKeyIs(step, value):
    if world.structure in [True, False]:
        assert unicode(world.structure).lower() == value
    else:
        assert world.structure == value


# assert the current `world.structure' is a reference to `value'
@step(u'Then it is a reference to "([^"]*)"')
def isAReferenceTo(step, value):
    assert world.structure == { "Ref" : value }


# assert the default value for a parameter is `value'
@step(u'Then its default is "([^"]*)"')
def itsDefaultIs(step, value):
    assert world.structure['Default'] == value


# parse from the securitygroup whose name is `securitygroup_name'
@step(u'And that has a securitygroup called "([^"]*)"')
def thatHasASecurityGroup(step, securitygroup_name):
    world.structure = world.structure['Resources'][securitygroup_name]


# validate Security Group Egress/Ingress rules
@step(u'Then traffic can "([^"]*)" the securitygroup on "([^"]*)" port "([^"]*)" (from|to) "([^"]*)"')
# List of parameters:
#   `<direction>, <ipprotocol>, <port>, <fromto>, <target>'
#   Notes:
#     - `direction' should be either `egress' or `ingress'
#     - `port' can be a single value or a range of two values delimited by the ` to ' string, e.g.: "80 to 81"
#     - `fromto' is only used in the decorator's regexp, but its logic is validated in the function such as:
#         - `fromto' must be equal to `to' in egress directions
#         - `fromto' must be equal to `from' in ingress directions
#     - `target' can be:
#         - a CidrIp
#         - a reference to a CidrIp (e.g. a template parameter)
#         - a reference to a [Destination|Source]SecurityGroupId
def thenCheckSecurityGroupRulesAre(step, direction, ipprotocol, port, fromto, target):

    # validate `fromto' logic
    if direction == 'egress':
        if fromto != 'to':
            assert False, '`fromto\' must be equal to `to\' in an egress direction.'
    elif direction == 'ingress':
        if fromto != 'from':
            assert False, '`fromto\' must be equal to `from\' in an ingress direction.'

    # whether FromPort and ToPort values are within a range or if they are the same value
    try:
        fromport, toport = port.replace(' ', '').split('to')
    except ValueError:
        fromport = port
        toport = port

    # determine if direction is egress or ingress
    if direction == 'egress':

        # set the pointer to the Egress section
        parameters_from_template = world.structure['Properties']['SecurityGroupEgress']
    elif direction == 'ingress':

        # set the pointer to the Ingress section
        parameters_from_template = world.structure['Properties']['SecurityGroupIngress']

    # set rule_matches variable to False by default
    rule_matches = False

    # parse parameters from the template
    for num, val in enumerate(parameters_from_template):
        ipprotocol_template =  parameters_from_template[num]['IpProtocol']
        fromport_template =  parameters_from_template[num]['FromPort']
        toport_template =  parameters_from_template[num]['ToPort']

        target_template = ''
        try:
            target_template =  parameters_from_template[num]['CidrIp']
        except KeyError:

            # if CidrIp is not found then:
            #   - determine if direction is egress or ingress
            #   - check for either DestinationSecurityGroupId or for SourceSecurityGroupId
            if direction == 'egress':
                try:
                    target_template =  parameters_from_template[num]['DestinationSecurityGroupId']
                except KeyError:
                    print 'DestinationSecurityGroupId not found.'
            if direction == 'ingress':
                try:
                    target_template =  parameters_from_template[num]['SourceSecurityGroupId']
                except KeyError:
                    print 'SourceSecurityGroupId not found.'

        # check if CidrIp or [Destination|Source]SecurityGroupId values are references in the template
        target_template_is_reference = False
        if target_template == { "Ref" : target }:
            target_template_is_reference = True

        # scan [Egress|Ingress] rules and exit the loop if a matching one is found 
        if ipprotocol_template == ipprotocol \
                and fromport_template == fromport \
                and toport_template == toport \
                and (target_template == target or target_template_is_reference):
            rule_matches = True
            break
    assert rule_matches
