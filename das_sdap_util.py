import json

from das_sdap_argparse import *


def asset_init(asset_type):
    if not asset_type:
        ValueError('资产类型不能为空')
    if asset_type == 'SOURCE_CODE':
        address = args.address
        repository = args.repository
        branch = args.branch
        language = args.language
        return {
            'type': asset_type,
            'address': address,
            'repository': repository,
            'branch': branch,
            'lang': language
        }
    elif asset_type == 'HOST':
        target = args.ips_word
        port = args.port
        return {
            'type': asset_type,
            'target': target,
            'port': port
        }
    elif asset_type == 'WEB':
        web_url = args.web_url
        language = args.language
        return {
            'type': asset_type,
            'webUrl': web_url,
            'lang': language
        }
    elif asset_type == 'APP':
        platform = args.platform
        package = args.package
        return {
            'type': asset_type,
            'platform': platform,
            '_package': package
        }



def write_file(context, file_path):
    if not file_path:
        return
    # 将结果输出到文件
    with open(file_path, "w") as file:
        file.write(context)


def read_json_for_file(file_path):
    if not file_path:
        return
    with open(file_path.name, 'r') as file:
        return json.load(file)


def read_task_ids_for_file(file_path):
    json_obj = read_json_for_file(file_path)
    tasks = json_obj['task']
    task_ids = {task['id'] for task in tasks}
    return list(task_ids)
