from lettuce import *
import ipaddr

def getRelevantRules(direction, instance_name, target, protocol, port=None):
    instance = world.template['Resources'][instance_name]
    assert instance['Type'] == "AWS::EC2::Instance", "%s is not an EC2 Instance" % instance_name
    
    security_groups = [ x['Ref'] for x in instance['Properties']['SecurityGroupIds'] ]

    rules = []
    for sg_name in security_groups:
        sg = world.template['Resources'][sg_name]
        assert sg['Type'] == "AWS::EC2::SecurityGroup"
        for rule in sg['Properties']['SecurityGroup' + direction.title()]:
            rules.append(rule)
    
    # Keep the protocol we care about
    rules = [ x for x in rules if x['IpProtocol'] == protocol ] 

    # Keep the networks that we care about
    rules = [ x for x in rules if ipaddr.IPAddress(target) in ipaddr.IPNetwork(x['CidrIp']) ]

    if port is not None:
        # Keep rules that are within a port range
        rules = [ x for x in rules if int(x['FromPort']) <= port <= int(x['ToPort']) ]

    return rules

# Outbound pings
@step(u'Then I (can|cannot) ping "([^"]*)" from an EC2 instance called "([^"]*)"')
def pingFromEc2Instance(step, capability, target, instance_name):

    rules = getRelevantRules(direction = 'egress',
                             instance_name = instance_name,
                             target = target,
                             protocol = 'icmp')

    # This statement is true or false based on if we get rules back.
    if capability == 'can':
        assert len(rules) > 0, "There are no security group rules that allow this traffic."
    if capability == 'cannot': 
        assert len(rules) == 0, "There is a security group rule that allows this traffic."
    

# Inbound pings
@step(u'Then I (can|cannot) ping an EC2 instance called "([^"]*)" from "([^"]*)"')
def pingEc2Instance(step, capability, instance_name, target):
    rules = getRelevantRules(direction = 'ingress',
                             instance_name = instance_name,
                             target = target,
                             protocol = 'icmp')

    # This statement is true or false based on if we get rules back.
    if capability == 'can':
        assert len(rules) > 0, "There are no security group rules that allow this traffic."
    if capability == 'cannot': 
        assert len(rules) == 0, "There is a security group rule that allows this traffic."


# Outbound network stuff
@step(u'Then I (can|cannot) access "([^"]*)" on "([^"]*)" port "([^"]*)" from an EC2 instance called "([^"]*)"')
def accessFromInstance(step, capability, target, protocol, port, instance_name): 
    rules = getRelevantRules(direction = 'egress',
                             instance_name = instance_name,
                             target = target,
                             protocol = protocol,
                             port = int(port))

    # This statement is true or false based on if we get rules back.
    if capability == 'can':
        assert len(rules) > 0, "There are no security group rules that allow this traffic."
    if capability == 'cannot': 
        assert len(rules) == 0, "There is a security group rule that allows this traffic."

# Inbound network stuff
@step(u'Then I (can|cannot) access an EC2 instance called "([^"]*)" on "([^"]*)" port "([^"]*)" from "([^"]*)"')
def accessFromInstance(step, capability, instance_name, protocol, port, target): 
    rules = getRelevantRules(direction = 'ingress',
                             instance_name = instance_name,
                             target = target,
                             protocol = protocol,
                             port = int(port))

    # This statement is true or false based on if we get rules back.
    if capability == 'can':
        assert len(rules) > 0, "There are no security group rules that allow this traffic."
    if capability == 'cannot': 
        assert len(rules) == 0, "There is a security group rule that allows this traffic."
