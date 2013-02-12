from lettuce import *
import ipaddr

# retrieve/derive security group rules from EC2 instance/SecurityGroup resources
def getRelevantRules(direction, source, source_type, target, protocol, port=None):
    protocol = protocol.lower()
    rules = []

    # source type: EC2Instance
    if source_type == 'EC2Instance':
        instance_name = source
        instance = world.template['Resources'][instance_name]
        assert instance['Type'] == "AWS::EC2::Instance", "%s is not an EC2 Instance" % instance_name

        security_groups = [ x['Ref'] for x in instance['Properties']['SecurityGroupIds'] ]
        for sg_name in security_groups:
            sg = world.template['Resources'][sg_name]
            assert sg['Type'] == "AWS::EC2::SecurityGroup"
            for rule in sg['Properties']['SecurityGroup' + direction.title()]:
                rules.append(rule)

    # source type: SecurityGroup
    elif source_type == 'SecurityGroup':
        security_group_name = source
        sg = world.template['Resources'][security_group_name]
        assert sg['Type'] == "AWS::EC2::SecurityGroup"
        for rule in sg['Properties']['SecurityGroup' + direction.title()]:
            rules.append(rule)

    # Keep the protocol we care about
    # pre-filter ICMP to see if desired types and codes have been specified for pings
    if protocol == 'icmp':
        rules_all_icmp = []
        for a in rules:
            # check if all ICMP traffic is permitted first
            if a['FromPort'] == str(-1) and a['ToPort'] == str(-1):
                rules_all_icmp.append(a)
        if len(rules_all_icmp) > 0:
            rules = rules_all_icmp
        # otherwise check if selected ICMP traffic has been configured instead
        else:
            echo_request = False
            echo_reply = False
            rules_selected_icmp = []
            
            # check for selected outbound ICMP traffic
            if direction == 'egress':
                # check if echo request and echo reply have both been configured in egress
                for a in rules:
                    if a['FromPort'] == str(8) and a['ToPort'] == str(-1):
                        echo_request = True
                        rules_selected_icmp.append(a)
                    if a['FromPort'] == str(0) and a['ToPort'] == str(-1):
                        echo_reply = True
                        rules_selected_icmp.append(a)
                if echo_request == True and echo_reply == True:
                    rules = rules_selected_icmp
                else:
                    rules = []

            # check for selected inbound ICMP traffic
            elif direction == 'ingress':
                # check if echo request has been configured in ingress
                for a in rules:
                    if a['FromPort'] == str(8) and a['ToPort'] == str(-1):
                        echo_request = True
                        rules_selected_icmp.append(a)
                if echo_request == True:
                    rules = rules_selected_icmp
                else:
                    rules = []
    else:
        # if protocol is not ICMP, add rules that match the specified protocol
        rules = [ x for x in rules if x['IpProtocol'] == protocol ]

    # Keep the networks that we care about
    # create a new list to handle exceptions when case-specific keys are not present
    rules_cidrip_secgroup = []
    for a in rules:
        try:
            if ipaddr.IPAddress(target) in ipaddr.IPNetwork(a['CidrIp']):
                rules_cidrip_secgroup.append(a)
        except:
            if direction == 'egress':
                try:
                    if a['DestinationSecurityGroupId']['Ref'] == target:
                        rules_cidrip_secgroup.append(a)
                except KeyError:
                    pass
            elif direction == 'ingress':
                try:
                    if a['SourceSecurityGroupId']['Ref'] == target:
                        rules_cidrip_secgroup.append(a)
                except KeyError:
                    pass
    rules = rules_cidrip_secgroup

    if port is not None:
        # Keep rules that are within a port range
        rules = [ x for x in rules if int(x['FromPort']) <= port <= int(x['ToPort']) ]

    return rules


# assertion logic
def assertByCapabilityAndRules(capability, rules):
    # This statement is true or false based on if we get rules back.
    if capability == 'can':
        assert len(rules) > 0, "There are no security group rules that allow this traffic."
    if capability == 'cannot':
        assert len(rules) == 0, "There is a security group rule that allows this traffic."


# Outbound pings - ping an IP address from an EC2 instance
@step(u'Then I (can|cannot) ping "([^"]*)" from an EC2 instance called "([^"]*)"')
def pingFromEc2Instance(step, capability, target, instance_name):
    rules = getRelevantRules(direction = 'egress',
                             source = instance_name,
                             source_type = 'EC2Instance',
                             target = target,
                             protocol = 'icmp')
    assertByCapabilityAndRules(capability, rules)


# Outbound pings - whether pings to an IP address are allowed by a source security group rule
@step(u'Then I (can|cannot) ping "([^"]*)" from the "([^"]*)" security group')
def pingFromSecurityGroupRule(step, capability, target, security_group_name):
    rules = getRelevantRules(direction = 'egress',
                             source = security_group_name,
                             source_type = 'SecurityGroup',
                             target = target,
                             protocol = 'icmp')
    assertByCapabilityAndRules(capability, rules)


# Inbound pings - ping an EC2 instance from a source IP address
@step(u'Then I (can|cannot) ping an EC2 instance called "([^"]*)" from "([^"]*)"')
def pingEc2Instance(step, capability, instance_name, target):
    rules = getRelevantRules(direction = 'ingress',
                             source = instance_name,
                             source_type = 'EC2Instance',
                             target = target,
                             protocol = 'icmp')
    assertByCapabilityAndRules(capability, rules)


# Inbound pings - the SecurityGroup allows incoming pings from a specified source IP address
@step(u'Then I (can|cannot) ping an EC2 instance behind the "([^"]*)" security group from "([^"]*)"')
def pingSecurityGroupEc2Instance(step, capability, security_group_name, target):
    rules = getRelevantRules(direction = 'ingress',
                             source = security_group_name,
                             source_type = 'SecurityGroup',
                             target = target,
                             protocol = 'icmp')
    assertByCapabilityAndRules(capability, rules)


# Outbound - connect to host-port from EC2 instance
@step(u'Then I (can|cannot) access "([^"]*)" on "([^"]*)" port "([^"]*)" from an EC2 instance called "([^"]*)"')
def accessFromEc2Instance(step, capability, target, protocol, port, instance_name):
    rules = getRelevantRules(direction = 'egress',
                             source = instance_name,
                             source_type = 'EC2Instance',
                             target = target,
                             protocol = protocol,
                             port = int(port))
    assertByCapabilityAndRules(capability, rules)


# Outbound - connect to host-port from a SecurityGroup rule
@step(u'Then I (can|cannot) access "([^"]*)" on "([^"]*)" port "([^"]*)" from the "([^"]*)" security group')
def accessFromSecurityGroupRule(step, capability, target, protocol, port, security_group_name):
    rules = getRelevantRules(direction = 'egress',
                             source = security_group_name,
                             source_type = 'SecurityGroup',
                             target = target,
                             protocol = protocol,
                             port = int(port))
    assertByCapabilityAndRules(capability, rules)


# Inbound - allow connect from host to port
@step(u'Then I (can|cannot) access an EC2 instance called "([^"]*)" on "([^"]*)" port "([^"]*)" from "([^"]*)"')
def accessEc2Instance(step, capability, instance_name, protocol, port, target):
    rules = getRelevantRules(direction = 'ingress',
                             source = instance_name,
                             source_type = 'EC2Instance',
                             target = target,
                             protocol = protocol,
                             port = int(port))
    assertByCapabilityAndRules(capability, rules)


# Inbound - allow connect from host to port based on a SecurityGroup rule
@step(u'Then I (can|cannot) access an EC2 instance behind the "([^"]*)" security group on "([^"]*)" port "([^"]*)" from "([^"]*)"')
def accessSecurityGroupEc2Instance(step, capability, security_group_name, protocol, port, target):
    rules = getRelevantRules(direction = 'ingress',
                             source = security_group_name,
                             source_type = 'SecurityGroup',
                             target = target,
                             protocol = protocol,
                             port = int(port))
    assertByCapabilityAndRules(capability, rules)
