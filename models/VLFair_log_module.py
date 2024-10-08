import sys
from os.path import dirname, abspath

d = dirname(dirname(abspath(__file__)))
sys.path.append(d)

FILE_PREFIX = 'VLFair/live_player_data/'


def getRegulationContent(list_qoe, list_bw, list_target_bw):
    i = 0
    log_content = ''
    for qoe_record in list_qoe:
        type = qoe_record['type']
        qoe = qoe_record['qoe']
        metrics = qoe_record['metrics']
        bw_before = list_bw[i]['bw']
        bw_after = list_target_bw[i]
        record = type + '\t' + str(qoe) + '\t' + str(metrics) + '\t' + str(bw_before) + '\t' + str(bw_after) + '\n'
        # print('record:', record)
        log_content += record
        i += 1

    return log_content


def doWrite(file, regulation_content):
    with open(FILE_PREFIX + file, 'a') as f:
        f.write(regulation_content)
