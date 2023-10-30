import os

import requests
import time
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

    response = requests.get(url + '/dipper-sso/api/user', headers={X_API_HEADER_KEY: x_api_key})
    check_response(response)
    set_key(ENV_PATH, URL, url)
    set_key(ENV_PATH, X_API_KEY, x_api_key)


def upload_file(file_path):
    file_path = file_path.name
    response = requests.post(get_url('/api/system/file/upload'), files={'file': (file_path, open(file_path, 'rb'))},
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

    if file_path:
        file_key = upload_file(file_path)

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
    response = requests.post(get_url('/api/asset/dispatch'), headers=default_headers_json(), data=json_body)
    data = check_response(response)
    write_file(json.dumps(data), args.out_path)


def task_state(task_id):
    response = requests.get(get_url('/api/task/state/' + str(task_id)), headers=default_headers())
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
        time.sleep(5)  # 如果状态不是成功、错误或停止，则等待一段时间后继续轮询


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
    response = requests.post(get_url('/api/report/export'), headers=default_headers_json(), data=json_body)
    data = check_response(response)
    return data


def report_state(report_id):
    response = requests.post(get_url('/api/report/' + str(report_id)), headers=default_headers())
    data = check_response(response)
    return data


def download_file(file_key, out_path):
    response = requests.get(get_url('/api/system/file/download/' + file_key), stream=True)
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
    response = requests.get(get_url('/api/project/overview/vul'), params=params, headers=default_headers())
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
