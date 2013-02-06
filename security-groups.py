from lettuce import *

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
