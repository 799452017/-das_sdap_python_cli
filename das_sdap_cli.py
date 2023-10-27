from dotenv import load_dotenv

from das_sdap_http_util import *

method_map = {
    'init': init_config,
    'scan': sent_scan,
    'wait_scan': wait_scan,
    'wait_report': wait_report,
    'print_result': print_result
}

if __name__ == '__main__':
    args = parser.parse_args()
    # 加载当前目录下.env文件获取配置
    load_dotenv(ENV_PATH)
    # 根据第一个参数获取调用方法的映射
    selected_method = method_map[args.method]
    selected_method()
