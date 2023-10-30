## 使用示例

+ 初始化配置

  ```shell
  ./das_sdap_cli init -url [平台地址] -k [用户apikey]
  ```

  init通过后，会在当前目录生成一个.env文件夹，用于存放配置信息

+ 发送扫描

  ```shell
  ./das_sdap_cli scan -at SOURCE_CODE -addr https://gitee.com/jflyfox/jfinal_cms.git -bra master -pn BLACKG.CHEN -tn python脚本测试任务 -an python资产测试 -lang JAVA_MAVEN -stray_id 10192 -f 123.txt -o scan_result.json
  ```

  表示发创建起了一个源代码资产，并将返回信息输出位scan_result.json文件， 任务详情参数请看./das_sdap_cli -h

+ 等待扫描

  ```shell
  ./das_sdap_cli wait_scan -f scan_result.json
  ```

+ 等待报告导出

  ```shell
  ./das_sdap_cli wait_report -f scan_result.json
  ```

+ 打印结果

  ```shell
  ./das_sdap_cli print_result -f scan_result.json
  ```

  

## 关于打包

下是使用 PyInstaller 打包适用于 macOS、Windows、Linux x86 和 ARM64 平台的 Python 脚本的步骤：

首先，确保在你的开发环境中安装了 PyInstaller。在终端或命令提示符中运行以下命令：

+ PyInstaller

  ```shell
  pip install pyinstaller
  ```

然后，进入到你的 Python 脚本所在的目录。

使用 PyInstaller 打包脚本为可执行文件。以下是针对不同平台的打包命令示例：

+ macOS：

  ```shell
  pyinstaller --onefile das_sdap_cli.py
  ```

+ Windows：

  ```shell
  pyinstaller --onefile das_sdap_cli.py
  ```

+ Linux x86：'

  ```shel
  pyinstaller --onefile --platform=linux das_sdap_cli.py
  ```

+ Linux ARM64：

  ```shell
  pyinstaller --onefile --platform=linux_arm64 das_sdap_cli.py
  ```

在每个平台上，这些命令将在 dist 目录下生成一个可执行文件。

请注意，根据你的开发环境和操作系统，可能需要在特定平台上进行打包。例如，在 macOS 上打包可用于 Windows 或 Linux 的可执行文件时，可能需要通过交叉编译或在相应的操作系统上进行打包。

另外，确保你的脚本和依赖项在跨平台环境中能够正常工作，并进行充分的测试以确保在不同平台上的兼容性。