from lettuce import *

@step(u'Then there is (a|an) "([^"]*)" record called "([^"]*)" that points to "([^"]*)" with a "([^"]*)" TTL in the "([^"]*)" hosted zone.')
def recordsetValidation(step, a_an, type, name, value, ttl, hosted_zone_name):

    # check the AWS Resource type
    assert world.structure['Type'] == 'AWS::Route53::RecordSet'

    # move the pointer to the properties node
    world.structure = world.structure['Properties']

    # check record name
    name_is_reference = False
    if world.structure['Name'] == { 'Fn::Join' : [ '', [ name, '.', { 'Ref': hosted_zone_name }, '.'] ] }:
        name_is_reference = True
    if name == world.structure['Name'] or name_is_reference:
        assert True
    else:
        assert False

    # check value
    record_matches = False
    resource_records_from_template = world.structure['ResourceRecords']
    for num, val in enumerate(resource_records_from_template):
        if value == val:
            record_matches = True
            break
    assert record_matches

    # check TTL
    ttl_is_reference = False
    if world.structure['TTL'] == { 'Ref' : ttl }:
        ttl_is_reference = True
    if world.structure['TTL'] == ttl or ttl_is_reference:
        assert True
    else:
        assert False

    # check hosted zone
    hosted_zone_name_is_reference = False
    if world.structure['HostedZoneName'] == { 'Fn::Join' : [ '', [ { 'Ref' : hosted_zone_name }, '.' ] ] }:
        hosted_zone_name_is_reference = True
    if world.structure['HostedZoneName'] == hosted_zone_name or hosted_zone_name_is_reference:
        assert True
    else:
        assert False
