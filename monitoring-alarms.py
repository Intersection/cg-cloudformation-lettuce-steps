from lettuce import *

# validate alarm structure
@step(u'Then if "([^"]*)" "([^"]*)" for the "([^"]*)" "([^"]*)" resource is "([^"]*)" than "([^"]*)", goes back to normal or data is insufficient over "([^"]*)" periods of "([^"]*)" seconds each, then notify "([^"]*)".')
# List of parameters:
#   `<statistic>, <metric_name>, <resource_name>, <resource_type>, <comparison_operator>, <threshold>, <evaluation_periods>, <period>, <notify_sendto>'
#   Notes:
#     - `notify_sendto' can be a string or a comma-delimited list, and it will be validated for:
#         - AlarmActions,
#         - InsufficientDataActions
#         - OKActions
#       The `notify_sendto' parameter assumes all the values for the actions above are references in the template.
#     - `resource_type' can be e.g. `EC2', `RDS', `AS', `ELB'
def thenCheckAlarm(step, statistic, metric_name, resource_name, resource_type, comparison_operator, threshold, evaluation_periods, period, notify_sendto):

    # move the pointer to alarm properties
    world.structure = world.structure['Properties']

    # derive dimension_name and namespace suffix by resource_type
    if resource_type == 'EC2':
        dimension_name = 'InstanceId'
        namespace_suffix = 'EC2'
    elif resource_type == 'RDS':
        dimension_name = 'DBInstanceIdentifier'
        namespace_suffix = 'RDS'
    elif resource_type == 'AS':
        dimension_name = 'AutoScalingGroupName'
        namespace_suffix = 'EC2'
    elif resource_type == 'ELB':
        dimension_name = 'LoadBalancerName'
        namespace_suffix = 'ELB'

    # check the namespace is correct
    assert world.structure['Namespace'] == "AWS/" + namespace_suffix

    # check the statistic is correct
    assert world.structure['Statistic'] == statistic

    # check the metric is correct
    assert world.structure['MetricName'] == metric_name

    # check dimensions
    dimension_matches = False
    for num, val in enumerate(world.structure['Dimensions']):
        dimension_name_template = world.structure['Dimensions'][num]['Name']
        dimension_value_template = world.structure['Dimensions'][num]['Value']

        # check if dimension_value_template is a reference in the template
        dimension_value_template_is_reference = False
        if dimension_value_template == { "Ref" : resource_name }:
            dimension_value_template_is_reference = True

        if dimension_name_template == dimension_name \
                and (dimension_value_template == resource_name or dimension_value_template_is_reference):
            dimension_matches = True
            break
    assert dimension_matches

    # create an array from notify_sendto
    notify_sendto_array = notify_sendto.replace(' ', '').split(',')

    # check alarm actions
    for i, notify_sendto_item in enumerate(notify_sendto_array):

        # check each action and exit the loop when a valid one is found
        alarm_action_matches = False
        for num, val in enumerate(world.structure['AlarmActions']):
            alarm_action_template = world.structure['AlarmActions'][num]['Ref']
            if alarm_action_template == notify_sendto_item:
                alarm_action_matches = True
                break
        assert alarm_action_matches

    # check insufficient data actions
    for i, notify_sendto_item in enumerate(notify_sendto_array):

        # check each action and exit the loop when a valid one is found
        insufficientdata_action_matches = False
        for num, val in enumerate(world.structure['InsufficientDataActions']):
            insufficientdata_action_template = world.structure['InsufficientDataActions'][num]['Ref']
            if insufficientdata_action_template == notify_sendto_item:
                insufficientdata_action_matches = True
                break
        assert insufficientdata_action_matches

    # check OK actions
    for i, notify_sendto_item in enumerate(notify_sendto_array):

        # check each action and exit the loop when a valid one is found
        ok_action_matches = False
        for num, val in enumerate(world.structure['OKActions']):
            ok_action_template = world.structure['OKActions'][num]['Ref']
            if ok_action_template == notify_sendto_item:
                ok_action_matches = True
                break
        assert ok_action_matches

    # check if the comparison operator is correct
    comparison_operator = comparison_operator.replace(' ', '').lower()
    if comparison_operator == 'greater':
        assert world.structure['ComparisonOperator'] == 'GreaterThanThreshold'
    elif comparison_operator == 'less':
        assert world.structure['ComparisonOperator'] == 'LessThanThreshold'
    elif comparison_operator == 'greaterorequal':
        assert world.structure['ComparisonOperator'] == 'GreaterThanOrEqualToThreshold'
    elif comparison_operator == 'lessorequal':
        assert world.structure['ComparisonOperator'] == 'LessThanOrEqualToThreshold'

    # check if threshold value is correct
    assert world.structure['Threshold'] == threshold

    # check if evaluation periods value is correct
    assert world.structure['EvaluationPeriods'] == evaluation_periods

    # check if period value is correct
    assert world.structure['Period'] == period
