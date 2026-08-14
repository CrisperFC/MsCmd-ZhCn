# Windows CMD 模拟器

一个纯 Python 实现的 Windows CMD 命令行模拟器，提供虚拟文件系统和常用命令支持。

**注**：dist 文件夹里面是在 Windows 10 环境下打包的exe文件，适合帮助在Windows 10+没有Python环境下的用户使用。

## 功能特性

- **虚拟文件系统**：完整的 C 盘目录结构模拟，支持文件读写、目录操作
- **29+ 个 CMD 命令**：涵盖导航、文件操作、系统信息等常用命令
- **通配符支持**：支持 `*` 和 `?` 进行文件匹配
- **路径规范化**：智能处理相对路径、绝对路径和 `..` 导航
- **树形目录显示**：`tree` 命令可可视化查看目录结构
- **命令历史记录**：支持上下箭头浏览历史命令
- **逻辑运算符**：支持 `&&` 和 `||` 连接多个命令

## 安装要求

- Python 3.7+
- 无需额外依赖

## 快速开始

```bash
# 克隆或下载项目
cd cmd

# 运行模拟器
python main.py

# 运行测试
python -m unittest discover -s tests -v
```

## 支持的命令

### 导航命令
| 命令 | 说明 |
|------|------|
| `cd` | 切换目录 |
| `dir` | 列出目录内容 |
| `pwd` | 显示当前路径 |
| `cls` | 清屏 |

### 文件操作
| 命令 | 说明 |
|------|------|
| `copy` | 复制文件 |
| `del` | 删除文件 |
| `ren/rename` | 重命名文件 |
| `type` | 显示文件内容 |
| `mkdir/md` | 创建目录 |
| `rmdir/rd` | 删除目录 |
| `echo` | 显示/写入文本 |
| `more` | 逐页显示 |

### 搜索命令
| 命令 | 说明 |
|------|------|
| `tree` | 树形显示目录 |
| `find` | 在文件中搜索文本 |
| `where` | 查找文件位置 |

### 系统命令
| 命令 | 说明 |
|------|------|
| `ver` | 显示版本信息 |
| `date` | 显示日期 |
| `time` | 显示时间 |
| `systeminfo` | 系统信息 |
| `help` | 帮助信息 |
| `exit` | 退出模拟器 |

### 环境变量
| 命令 | 说明 |
|------|------|
| `set` | 设置/显示环境变量 |
| `path` | 显示/设置 PATH |
| `setx` | 永久设置环境变量 |
| `color` | 设置颜色 |
| `title` | 设置窗口标题 |
| `prompt` | 设置提示符 |

## 项目结构

```
cmd/
├── main.py                  # 主入口
├── shells/                  # Shell 层
│   └── cmd_shell.py         # 命令行交互界面
├── commands/                # 命令层
│   ├── base.py              # 命令基类
│   ├── navigation.py        # 导航命令
│   ├── file_ops.py          # 文件操作命令
│   ├── system.py            # 系统命令
│   └── utilities.py         # 工具命令
├── filesystem/              # 文件系统层
│   └── virtual_fs.py        # 虚拟文件系统
├── assets/                  # 资源文件
│   └── c_drive.json         # 初始文件系统数据
└── tests/                   # 测试文件
    ├── test_virtual_fs.py   # 文件系统测试
    └── test_commands.py     # 命令测试
```

## 架构说明

项目采用三层架构：

1. **文件系统层** (`filesystem/`)：VirtualFileSystem 提供文件操作接口
2. **命令层** (`commands/`)：各类命令继承 Command 基类实现具体逻辑
3. **Shell 层** (`shells/`)：CmdShell 处理用户输入并调度命令执行

## 使用示例

```cmd
C:> dir
C:> cd Windows
C:\Windows> tree
C:\Windows> find "test" file.txt
C:\Windows> where *.sys
C:\Windows> echo hello > test.txt
C:\Windows> type test.txt
C:\Windows> mkdir test\sub
C:\Windows> copy file.txt backup.txt
```

## 运行测试

```bash
# 运行所有测试
python -m unittest discover -s tests -v

# 运行单个测试文件
python -m unittest tests.test_virtual_fs

# 运行简单测试
python test_simple.py
```

## 联系方式

TEL.: 18770020040

WECHAT: 18770020040

感谢使用本项目！如果您有任何问题或需要进一步的帮助，请随时联系。祝编程愉快！ 🚀
