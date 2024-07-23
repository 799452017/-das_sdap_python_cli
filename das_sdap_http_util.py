import os

import requests
import time
import operator

from dotenv import set_key
from tabulate import tabulate

from constans import *
from das_sdap_util import *

class APIError(Exception):
    pass


'''
校验response信息
'''


def check_response(response):
    url = response.request.url
    if response.status_code == 200 and response.json()['code'] == 200:
        print(url + ' 请求成功！')
        print('返回内容:', response.text)
        return response.json()['data']
    else:
        print(url + ' 请求失败！')
        raise APIError('错误信息:', response.text)


def get_url(path):
    url = os.environ.get(URL)
    if not url:
        raise ValueError('url为空，未初始化配置')
    return url + path


def default_headers_json():
    headers = default_headers()
    headers['Content-Type'] = 'application/json'
    return headers


def default_headers():
    apikey = os.environ.get(X_API_KEY)
    if not apikey:
        raise ValueError('apikey为空，未初始化配置')
    return {
        X_API_HEADER_KEY: apikey
    }


'''
初始化配置
根据携带的url及已认证信息调用户信息接口
调用成功则将参数写入系统环境变量中
'''


def init_config():
    url = args.url
    if not url:
        raise ValueError('url不能为空')
    url = url.rstrip('/')
    x_api_key = args.apikey

    response = requests.get(url + '/dipper-sso/api/user', verify=False, headers={X_API_HEADER_KEY: x_api_key})
    check_response(response)
    set_key(ENV_PATH, URL, url)
    set_key(ENV_PATH, X_API_KEY, x_api_key)


def upload_file_():
    file_path = args.file_path
    file_key = upload_file(file_path)
    out_path = args.out_path
    write_file(file_key, out_path)


def upload_file(file_path):
    file_path = file_path.name
    response = requests.post(get_url('/api/system/file/upload'), verify=False, files={'file': (file_path, open(file_path, 'rb'))},
                             headers=default_headers())
    data = check_response(response)
    return data['key']


def sent_scan():
    file_key = None
    asset_name = args.asset
    project_name = args.project
    task_name = args.task_name
    strategy_id = args.strategy_id
    asset_type = args.asset_type
    username = args.username
    password = args.password
    credential_id = args.credential_id
    parameters = get_parameters()
    file_path = args.file_path
    file_key_arg = args.file_key
    file_key_path = args.file_key_path

    if file_path:
        file_key = upload_file(file_path)
    elif file_key_arg:
        file_key = file_key_arg
    elif file_key_path:
        file_key = read_json_for_file(file_key_path)

    body = {
        'name': asset_name,
        'projectName': project_name,
        'strategyId': [strategy_id],
        'taskName': task_name,
        'asset': asset_init(asset_type),
        'fileKey': file_key,
        'credentialId': credential_id,
        'auth': {
            'type': 'ACCOUNT',
            'username': username,
            'password': password
        },
        'parameters': parameters
    }
    json_body = json.dumps(body)
    response = requests.post(get_url('/api/asset/dispatch'), verify=False, headers=default_headers_json(), data=json_body)
    data = check_response(response)
    write_file(json.dumps(data), args.out_path)


def task_state(task_id):
    response = requests.get(get_url('/api/task/state/' + str(task_id)), timeout=None, verify=False, headers=default_headers())
    data = check_response(response)
    return data[0]


def wait_scan():
    task_id = read_task_ids_for_file(args.file_path)[0]
    while True:
        task = task_state(task_id)
        state = task['state']

        if state == 'SUCCESS':
            write_file(task, args.out_path)
            return task

        if state in ('ERROR', 'STOP'):
            raise APIError(f'任务异常终止 {state} ')

        print('任务执行中..')
        time.sleep(15)  # 如果状态不是成功、错误或停止，则等待一段时间后继续轮询


def export_report(report_name, scan_id):
    body = {
        "reportName": report_name,
        "watermark": "",
        "scanId": [scan_id],
        "risk": [
            "critical",
            "high",
            "medium",
            "low"
        ],
        "format": [
            "WORD",
            "PDF",
            "EXCEL"
        ]
    }

    json_body = json.dumps(body)
    response = requests.post(get_url('/api/report/export'), verify=False, headers=default_headers_json(), data=json_body)
    data = check_response(response)
    return data


def report_state(report_id):
    response = requests.post(get_url('/api/report/' + str(report_id)), verify=False, headers=default_headers())
    data = check_response(response)
    return data


def download_file(file_key, out_path):
    download_url = get_url('/api/system/file/download/' + file_key)
    print('报告下载链接：' + download_url)
    response = requests.get(download_url, verify=False, stream=True)
    response.raise_for_status()

    with open(out_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)


def wait_report():
    task_id = read_task_ids_for_file(args.file_path)[0]
    print(task_id)
    task = task_state(task_id)
    scan_id = task['scanId']
    task_name = task['taskName']
    report = export_report(task_name, scan_id)
    report_id = report['id']

    while True:
        retport_vo = report_state(report_id)
        state = retport_vo['state']

        if state == 'SUCCESS':
            download_file(retport_vo['fileKey'], args.out_path)
            return task

        if state == 'FAILED':
            raise APIError(f"报告导出异常终止 {state} state")

        print('报告导出中..')
        time.sleep(5)


def get_scan():
    task_id = read_task_ids_for_file(args.file_path)[0]
    return task_state(task_id)['scanId']


def print_result():
    scan_id = get_scan()
    params = {
        'scanId': scan_id,
        'repeat': 'true'
    }
    response = requests.get(get_url('/api/project/overview/vul'), verify=False, params=params, headers=default_headers())
    data = check_response(response)
    print(data)
    vul_risk_data = [
        ['风险等级', '数量'],
        ['超危', data['criticalCount']],
        ['高危', data['highCount']],
        ['中危', data['mediumCount']],
        ['低危', data['lowCount']],
        ['信息', data['infoCount']]
    ]
    table_info = tabulate(vul_risk_data, headers='firstrow', tablefmt="simple")
    print(table_info)

    if args.out_path:
        vul_stats = {
            "status": "success",
            "metrics": {
                "criticalCount": data['criticalCount'],
                "highCount": data['highCount'],
                "mediumCount": data['mediumCount'],
                "lowCount": data['lowCount'],
                "infoCount": data['infoCount']
            }
        }
        write_file(vul_stats, args.out_path)
    return data
def sec_gate():
    vuln_stats = print_result()
    c = vuln_stats['criticalCount']
    h = vuln_stats['highCount']
    m = vuln_stats['mediumCount']
    l = vuln_stats['lowCount']
    i = vuln_stats['infoCount']

    a_i, a_l, a_m, a_h, a_c = args.info, args.low, args.medium, args.high, args.critical
    gate_type = args.gate_type

    # 门禁条件和结果存储
    gates = {
        '超危': {'count': c, 'threshold': a_c, 'result': '-'},
        '高危': {'count': h, 'threshold': a_h, 'result': '-'},
        '中危': {'count': m, 'threshold': a_m, 'result': '-'},
        '低危': {'count': l, 'threshold': a_l, 'result': '-'},
        '信息': {'count': i, 'threshold': a_i, 'result': '-'},
    }

    # 根据门禁类型进行判断
    for risk_level, gate in gates.items():
        if gate['threshold'] is not None:
            if gate_type == '<=':
                gate['result'] = '✓' if operator.le(gate['count'], gate['threshold']) else 'x'
            elif gate_type == '<':
                gate['result'] = '✓' if operator.lt(gate['count'], gate['threshold']) else 'x'
            elif gate_type == '=':
                gate['result'] = '✓' if operator.eq(gate['count'], gate['threshold']) else 'x'

    # 打印门禁信息
    sec_gate_info = [
        ['风险等级', '门禁', '结果'],
        *[
            [risk_level, f'| {gate["count"]} {gate_type} {gate["threshold"]}', f'|  {gate["result"]}']
            for risk_level, gate in gates.items()
        ]
    ]

    table_info = tabulate(sec_gate_info, headers='firstrow', tablefmt="simple")
    print(table_info)

    # 检查结果中是否包含任意一个 'x'
    block = False
    for gate in gates.values():
        if 'x' in gate['result']:
            block = True
            if not args.gate_block:
                raise ValueError("安全质量门禁不通过，流程阻断！")
            else:
                print("安全质量门禁不通过! 流程不阻断")

    if not block:
        print("恭喜你！安全质量门禁通过")

