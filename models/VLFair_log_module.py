import sys
import time
from os.path import dirname, abspath

d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

FILE_PREFIX = 'VLFair/live_player_data/'


def getRegulationContent(list_qoe, list_bw, list_target_bw):
    try:
        i = 0
        log_content = ''
        for qoe_record in list_qoe:
            type = qoe_record['type']
            qoe = qoe_record['qoe']
            metrics = qoe_record['metrics']
            bw_before = list_bw[i]['bw']
            bw_after = list_target_bw[i]
            t = int(time.time())
            record = type + '\t' + str(qoe) + '\t' + str(metrics) + '\t' + str(round(bw_before, 2)) + '\t' + str(
                round(bw_after, 2)) + '\t' + str(t) + '\n'
            # print('record:', record)
            log_content += record
            i += 1

        return log_content
    except Exception as e:
        print(f"xxxtest getRegulationContent")


def doWrite(file, regulation_content):
    with open(FILE_PREFIX + file, 'a') as f:
        f.write(regulation_content)


def get_all_records(file):
    all_record = []
    with open(FILE_PREFIX + file, 'r') as f:
        for record in f.readlines():
            all_record.append(record)
    return all_record


def divide_records_dic_by_type(all_record):
    records_dic = {}
    records_dic['vod'] = []
    records_dic['live'] = []
    for record in all_record:
        type = record.split('\t')[0]
        records_dic[type].append(record)
    return records_dic


def get_records_by_type(type, records_dic):
    target_records = records_dic[type]
    result_list = []
    for record in target_records:
        record_dic = {}
        elements = record.split('\t')
        metrics = eval(elements[2])
        record_dic['type'] = elements[0]
        record_dic['qoe'] = elements[1]
        record_dic['PQ'] = metrics['PQ']
        record_dic['rebuffer'] = metrics['rebuffer']
        record_dic['smoothness'] = metrics['smoothness']
        record_dic['latency'] = metrics['latency']
        record_dic['bw_before'] = elements[3]
        record_dic['bw_after'] = elements[4]
        record_dic['timestamp'] = elements[5]
        result_list.append(record_dic)
    return result_list
