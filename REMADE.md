下是使用 PyInstaller 打包适用于 macOS、Windows、Linux x86 和 ARM64 平台的 Python 脚本的步骤：

首先，确保在你的开发环境中安装了 PyInstaller。在终端或命令提示符中运行以下命令：

pip install pyinstaller

然后，进入到你的 Python 脚本所在的目录。

使用 PyInstaller 打包脚本为可执行文件。以下是针对不同平台的打包命令示例：

macOS：

pyinstaller --onefile das_sdap_cli.py

Windows：

pyinstaller --onefile das_sdap_cli.py

Linux x86：

pyinstaller --onefile --platform=linux das_sdap_cli.py

Linux ARM64：

pyinstaller --onefile --platform=linux_arm64 das_sdap_cli.py

在每个平台上，这些命令将在 dist 目录下生成一个可执行文件。

请注意，根据你的开发环境和操作系统，可能需要在特定平台上进行打包。例如，在 macOS 上打包可用于 Windows 或 Linux 的可执行文件时，可能需要通过交叉编译或在相应的操作系统上进行打包。

另外，确保你的脚本和依赖项在跨平台环境中能够正常工作，并进行充分的测试以确保在不同平台上的兼容性。