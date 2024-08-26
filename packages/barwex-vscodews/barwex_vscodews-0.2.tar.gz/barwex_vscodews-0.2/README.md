vscode 默认保存的工作区文件后缀名为 .code-workspace，直接保存到桌面很难看。
所以弄了个简单的脚本，在桌面上创建工作区快捷方式。

系统：Deepin23

安装：pip install barwex-vscodews

为项目工作区创建桌面入口：barwe-vscodews -n API -d /path/to/your/api/dir/

生产的工作区快捷方式以 $ 开头，使用与 vscode 一致的图标。