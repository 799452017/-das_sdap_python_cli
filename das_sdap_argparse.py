import argparse


def parse_map_arg(arg):
    """
    解析键值对的参数并返回字典
    """
    try:
        key, value = arg.split("=")
        return {key: value}
    except ValueError:
        raise argparse.ArgumentTypeError("参数格式无效，应为key=value")


def get_parameters():
    # 使用map参数
    if args.parameters:
        my_map = {}
        for item in args.parameters:
            my_map.update(item)
        return my_map


parser = argparse.ArgumentParser()
parser.add_argument('method', choices=['init', 'scan', 'wait_scan', 'wait_report', 'print_result'], type=str,
                    help='调用方法')
parser.add_argument('-url', '--url', type=str, help='DAS-SDAP服务地址')
parser.add_argument('-k', '--apikey', type=str, help='DAS-SDAP服务apikey')
parser.add_argument('-f', '--file_path', type=argparse.FileType('rb'), help='文件路径')
parser.add_argument('-pn', '--project', type=str, help='项目名称')
parser.add_argument('-an', '--asset', type=str, help='资产名称')
parser.add_argument('-tn', '--task_name', type=str, help='任务名称')
parser.add_argument('-at', '--asset_type', type=str, choices=['HOST', 'SOURCE_CODE', 'WEB', 'APP'], help='资产类型')
parser.add_argument('-addr', '--address', required=False, type=str, help='SOURCE_CODE资产地址')
parser.add_argument('-rep', '--repository', required=False, default='GIT', choices=['SVN', 'GIT'], type=str,
                    help='SOURCE_CODE资产仓库类型')
parser.add_argument('-bra', '--branch', required=False, type=str, default='master',
                    help='SOURCE_CODE资产仓库branch或tag')
languages = [
    'JAVA', 'JAVA_MAVEN', 'JAVA_GRADLE', 'JAVASCRIPT', 'C', 'C_SHARP', 'PYTHON', 'PHP', 'OBJ_C', 'COBOL', 'NODEJS',
    'KOTLIN', 'GOLANG', 'SCALA', 'RUBY', 'SWIFT', 'SHELL'
]
parser.add_argument('-lang', '--language', required=False, type=str, choices=languages, default='JAVA', help='资产语言')
parser.add_argument('-ips', '--ip_word', required=False, type=str, help='HOST资产IP段')
parser.add_argument('-port', required=False, type=str, help='HOST资产端口')
parser.add_argument('-web_url', '--web_url', required=False, type=str, help='WEB资产应用地址')
parser.add_argument('-plf', '--platform', required=False, type=str, choices=['IOS', 'ANDROID'], help='APP资产平台类型')
parser.add_argument('-pack', '--package', required=False, type=str, help='APP资产package包名')
parser.add_argument('-u', '--username', required=False, type=str, help='资产凭据账号')
parser.add_argument('-p', '--password', required=False, type=str, help='资产凭据密码')
parser.add_argument('-cred_id', '--credential_id', required=False, type=str, help='凭据编号，优先级大于资产凭据账号密码')
parser.add_argument('-stray_id', '--strategy_id', required=False, type=int, help='扫描策略编号')
parser.add_argument('-params', '--parameters', nargs='+', required=False, type=parse_map_arg,
                    help='扫描策略扩展参数，具体值依据策略填写')
parser.add_argument('-o', '--out_path', required=False, type=str, help='执行结果输出到文件')
args = parser.parse_args()
