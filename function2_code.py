import json
import boto3
import datetime
import os


def lambda_handler(event, context):
    # TODO implement

    region = os.environ["REGION"]
    print(region)
    _ec2_instances = instances_list(region)

    _responses = {'ec2': []}

    for _ec2_instance_id in _ec2_instances:
        try:
            print("Desliga alarme:", _ec2_instance_id)
            _res_alarm = disable_alarm([_ec2_instance_id], region)
            print("Desliga instancia:", _ec2_instance_id)
            _res = execute_ec2_stop(_ec2_instance_id, region)

            _responses['ec2'].append(_res_alarm)
            _responses['ec2'].append(_res)

        except Exception as ex:
            _error = {"instance_id": _ec2_instance_id, "error": ex.args}
            _responses['ec2'].append(_error)
            print(_error)
            pass

    return {
        'statusCode': 200,
        'body': json.dumps(_responses)
    }


def instances_list(_region):
    ec2_client = boto3.client('ec2', region_name=_region)
    response = ec2_client.describe_instances()

    instance_ids = []
    current_time = datetime.datetime.now()

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'running':
                tags = instance.get('Tags', [])
                #diarios
                auto_power_seg_tag = None
                auto_power_ter_tag = None
                auto_power_qua_tag = None
                auto_power_qui_tag = None
                auto_power_sex_tag = None
                auto_power_sab_tag = None
                auto_power_dom_tag = None
                #seg-sex e sab_dom
                auto_power_seg_sex_tag = None
                auto_power_sab_dom_tag = None
                #semanal
                auto_power_semana_tag = None

                for tag in tags:
                    if tag['Key'] == 'start_stop - seg':
                        auto_power_seg_tag = tag['Value']
                    elif tag['Key'] == 'start_stop - ter':
                        auto_power_ter_tag = tag['Value']
                    elif tag['Key'] == 'start_stop - qua':
                        auto_power_qua_tag = tag['Value']
                    elif tag['Key'] == 'start_stop - qui':
                        auto_power_qui_tag = tag['Value']
                    elif tag['Key'] == 'start_stop - sex':
                        auto_power_sex_tag = tag['Value']
                    elif tag['Key'] == 'start_stop - sab':
                        auto_power_sab_tag = tag['Value']
                    elif tag['Key'] == 'start_stop - dom':
                        auto_power_dom_tag = tag['Value']

                    elif tag['Key'] == 'start_stop - seg a sex':
                        auto_power_seg_sex_tag = tag['Value']
                    elif tag['Key'] == 'start_stop - sab/dom':
                        auto_power_sab_dom_tag = tag['Value']

                    elif tag['Key'] == 'start_stop - semana':
                        auto_power_semana_tag = tag['Value']
                   
                    
                #diarios
                if auto_power_seg_tag and check_same_day(current_time, 0):
                   
                    if not check_time_range(auto_power_seg_tag, current_time):
                        instance_ids.append(instance['InstanceId'])
                    continue
               
                if auto_power_ter_tag and check_same_day(current_time, 1):
                   
                    if not check_time_range(auto_power_ter_tag, current_time):
                       
                        instance_ids.append(instance['InstanceId'])
                    continue
             
                if auto_power_qua_tag and check_same_day(current_time, 2):
                 
                    if not check_time_range(auto_power_qua_tag, current_time):
                        instance_ids.append(instance['InstanceId'])
                    continue

                if auto_power_qui_tag and check_same_day(current_time, 3):
                   
                    if not check_time_range(auto_power_qui_tag, current_time):
                        instance_ids.append(instance['InstanceId'])
                    continue

                if auto_power_sex_tag and check_same_day(current_time, 4):
            
                    if not check_time_range(auto_power_sex_tag, current_time):
                        instance_ids.append(instance['InstanceId'])
                    continue

                if auto_power_sab_tag and check_same_day(current_time, 5):
      
                    if not check_time_range(auto_power_sab_tag, current_time):
                        instance_ids.append(instance['InstanceId'])
                    continue

                if auto_power_dom_tag and check_same_day(current_time, 6):
     
                    if not check_time_range(auto_power_dom_tag, current_time):
                        instance_ids.append(instance['InstanceId'])
                    continue
                #seg-sex   e    #sab-dom
                if auto_power_seg_sex_tag and check_same_day_seg_sex(current_time):
       
                    if not check_time_range(auto_power_seg_sex_tag, current_time):
                        instance_ids.append(instance['InstanceId'])
                    continue
                
                if auto_power_sab_dom_tag and check_same_day_sab_dom(current_time):
        
                    if  not check_time_range(auto_power_sab_dom_tag, current_time):
                        instance_ids.append(instance['InstanceId'])
                    continue
                #semanal
                if auto_power_semana_tag:
       
                    if  not check_time_range(auto_power_semana_tag, current_time):
                        instance_ids.append(instance['InstanceId'])
                    continue
                    

    return instance_ids

def subtract_hours(current_time, hours_to_subtract):
    return current_time - datetime.timedelta(hours=hours_to_subtract)

def check_time_range(time_range, current_time):
 
    current_time_brazil = subtract_hours(current_time, 3)
    start_time, end_time = time_range.split('-')

    start_hour, start_minute = map(int, start_time.split(':'))
    end_hour, end_minute = map(int, end_time.split(':'))

    start = datetime.datetime(current_time.year, current_time.month, current_time.day, start_hour, start_minute)
    end = datetime.datetime(current_time.year, current_time.month, current_time.day, end_hour, end_minute)

    return start <= current_time_brazil <= end

def check_same_day(current_time, function_day):
    
    current_time_brazil = subtract_hours(current_time, 3)
    current_day = current_time_brazil.weekday()

    return current_day == function_day

def check_same_day_seg_sex(current_time):
  
    current_time_brazil = subtract_hours(current_time, 3)
    current_day = current_time_brazil.weekday()

   
    if current_day < 5:
        return True
    else:
        return False

def check_same_day_sab_dom(current_time):
  
    current_time_brazil = subtract_hours(current_time, 3)
    current_day = current_time_brazil.weekday()

  
    if current_day > 4:
        return True
    else:
        return False

def filter_tag_name(_object: boto3) -> str:
    """
    Filter tag name
    :param _object: boto3 object
    :return: name set on tag
    """
    _name = ''
    try:
        if _object.tags is not None:
            for tag in _object.tags:
                if tag['Key'] == 'Name':
                    _name = tag['Value']
    except Exception as e:
        print(e.args, e)
        try:
            if _object['Tags'] is not None:
                for tag in _object['Tags']:
                    if tag['Key'] == 'Name':
                        _name = tag['Value']
        except Exception as e:
            print(e.args, e)
            pass
    return _name


def ec2_instance_stop(_ec2_instance_id: str, _region: str):
    """
    stop an instance
    :param _ec2_instance_id: id from instance
    :param _region: region  (ex: us-east-1)
    :return: 0 - no error
    """
    try:
        _ec2_resource = boto3.Session(region_name=_region).resource('ec2')
        _ec2_resource.Instance(_ec2_instance_id).stop()
    except Exception as ex:
        raise Exception(ex)
    return 0


def execute_ec2_stop(_ec2_instance_id: str, _region: str):
    # Try to stop the instance
    try:
        _res = ec2_instance_stop(_ec2_instance_id, _region)
    except Exception as ex:
        _time = datetime_to_str_pt_br(datetime.datetime.now())
        _err = '%s: Failed to stop instance %s, error: %s' % (_time, _ec2_instance_id, ex.args)
        print(_err)
        raise Exception(_err)

    # Try to get instance info
    try:
        _instance = get_ec2_instance_info(_ec2_instance_id, _region)
    except Exception as ex:
        _time = datetime_to_str_pt_br(datetime.datetime.now())
        _err = '%s: Failed to get status for instance %s, error: %s' % (_time, _ec2_instance_id, ex.args)
        print(_err)
        raise Exception(_err)

    _msg = '%s: Error on compiling instance %s info'

    try:
        if _res == 0:
            _instance_name = filter_tag_name(_instance)
            _instance_launch_time = datetime_to_str_pt_br(_instance.launch_time)
            _msg = 'Instance %s (%s) has been stoped, launch time: %s' % (_instance_name,
                                                                           _ec2_instance_id,
                                                                           _instance_launch_time)
        else:
            _msg = 'Instance %s has not been stoped' % _ec2_instance_id
    except Exception as ex:
        _time = datetime_to_str_pt_br(datetime.datetime.now())
        _err = _msg % (_time, _ec2_instance_id)
        print(_err)
        raise Exception(_err)

    print(_msg)

    return {'instance_id': _ec2_instance_id,
            'service': 'ec2-stop',
            'status': 'complete',
            'description': _msg}


def get_ec2_instance_info(_ec2_instance_id: str, _region: str):
    """
    Get information from instance
    :param _ec2_instance_id:
    :param _region:
    :return:
    """
    try:
        resource = boto3.Session(region_name=_region).resource('ec2')
        instance = resource.Instance(_ec2_instance_id)
    except Exception as ex:
        raise Exception(ex)
    return instance


def datetime_to_str_pt_br(_datetime: datetime.datetime):
    """
    Convert datetime object to pt-br datetime string
    :param _datetime: datetime
    :return: datetime string
    """
    _datetime = str(datetime.datetime.strftime(_datetime - datetime.timedelta(hours=3),
                                               '%d/%m/%Y %H:%M:%S'))
    return _datetime


def disable_alarm(_instance_ids: list, _region: str):
    try:
        _instance_alarms = filter_alarm_by_instance(_instance_ids, _region)
        disable_alarm_actions(_instance_alarms, _region)
        _time = datetime.datetime.now()
        _msg = '%s: Alarms from instance %s disabled' % (_time, _instance_ids)
    except Exception as ex:
        _time = datetime.datetime.now()
        _msg = '%s: Instance %s has no alarms set, error: %s' % (_time, _instance_ids, ex.args)
        raise Exception(_msg)
    return _msg


def filter_alarm_by_instance(_instance_ids: list, _region: str, _profile: str = None):
    _alarms = []
    try:
        _instances_alarm = describe_instances_alarms_set(_region=_region)
    except Exception as ex:
        raise Exception(ex)
    for _instance_alarm in _instances_alarm:
        if _instance_alarm['instance_id'] in _instance_ids:
            _alarms.append(_instance_alarm)
    return _alarms


def describe_instances_alarms_set(_metric_name: str = None, _region: str = 'us-east-2', _profile: str = None):
    """
    Describe alarms set for instances by metric name
    :param _metric_name: metric name, one of:
    :param _region: region (default us-east-2 (ohio))
    :param _profile: profile (optional)
    :return: instances list with the specified alarm for metric name
    """
    _cloudwatch_client = boto3.Session(region_name=_region).client('cloudwatch')
    _metric_alarms = _cloudwatch_client.describe_alarms(MaxRecords=100)
    _metric_alarms_list = _metric_alarms['MetricAlarms']
    while 'NextToken' in _metric_alarms:
        _metric_alarms = _cloudwatch_client.describe_alarms(MaxRecords=100, NextToken=_metric_alarms['NextToken'])
        _metric_alarms_list.extend(_metric_alarms['MetricAlarms'])
    _instances = []
    _instances_index = []
    for _item in _metric_alarms_list:
        if _item['MetricName'] == _metric_name or _metric_name is None:
            for _value in _item['Dimensions']:
                if _value['Name'] == 'InstanceId' and {'instance_id': _value['Value']} not in _instances:
                    _instances.append({'instance_id': _value['Value'],
                                       'alarms': [_item['AlarmName']]})
                    _instances_index.append(_value['Value'])
                elif _value['Name'] == 'InstanceId':
                    _ = _instances_index.index(_value['Value'])
                    _instances[_]['alarms'].append(_item['AlarmName'])
        else:
            pass
    return _instances


def disable_alarm_actions(_instance_alarms: list, _region: str = None, _profile: str = None):
    _cloudwatch_client = boto3.Session(region_name=_region).client('cloudwatch')
    for _instance_alarm in _instance_alarms:
        _cloudwatch_client.disable_alarm_actions(AlarmNames=_instance_alarm['alarms'])
