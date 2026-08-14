# Windows CMD Simulator

**Language** [English](en-us.md) [中文](../README.md)

A Windows CMD command-line simulator purely built with Python, equipped with a virtual file system and support for common commands.

**Note**: The dist folder contains executable files packaged under Windows 10. They are suitable for users on Windows 10+ without a local Python environment.

## Features

- **Virtual File System**: Complete simulated C drive directory structure, supporting file read/write and directory operations
- **29+ CMD Commands**: Covers navigation, file manipulation, system info and other daily-used commands
- **Wildcard Support**: Match files with `*` and `?`
- **Path Normalization**: Intelligently resolve relative paths, absolute paths and `..` back navigation
- **Tree Directory Preview**: Visualize folder structure via the `tree` command
- **Command History**: Scroll past commands with Up & Down arrow keys
- **Logical Operators**: Chain multiple commands using `&&` and `||`

## Requirements

- Python 3.7 or higher
- No extra dependencies required

## Quick Start

```bash
# Clone or download this project
cd cmd

# Launch the simulator
python main.py

# Run the test
python -m unittest discover -s tests -v
```

## Supported Commands

### Navigation Commands

| Command | Description                        |
| ------- | ---------------------------------- |
| `cd`    | Change working directory           |
| `dir`   | List contents of current directory |
| `pwd`   | Print current absolute path        |
| `cls`   | Clear console screen               |

### File Operations

| Command      | Description                       |
| ------------ | --------------------------------- |
| `copy`       | Copy target files                 |
| `del`        | Delete specified files            |
| `ren/rename` | Rename files or folders           |
| `type`       | Display text content of files     |
| `mkdir/md`   | Create new directory              |
| `rmdir/rd`   | Delete empty directory            |
| `echo`       | Output text or write text to file |
| `more`       | View file content page by page    |

### Search Commands

| Command | Description                          |
| ------- | ------------------------------------ |
| `tree`  | Print tree-style directory structure |
| `find`  | Search keyword text inside files     |
| `where` | Locate paths of matched files        |

### System Commands

| Command      | Description                   |
| ------------ | ----------------------------- |
| `ver`        | Show simulator version info   |
| `date`       | Display current date          |
| `time`       | Display current time          |
| `systeminfo` | Show simulated system details |
| `help`       | View command help docs        |
| `exit`       | Quit the simulator            |

### 环境变量

| Command  | Description                                  |
| -------- | -------------------------------------------- |
| `set`    | View or set temporary environment variables  |
| `path`   | Check or modify PATH variable                |
| `setx`   | Set persistent environment variables         |
| `color`  | Modify console foreground & background color |
| `title`  | Customize window title text                  |
| `prompt` | Change command prompt style                  |

## 项目结构

```
cmd/
├── main.py                  # Main program entry
├── shells/                  # Shell interactive layer
│   └── cmd_shell.py         # CMD interactive terminal logic
├── commands/                # Command logic layer
│   ├── base.py              # Base abstract command class
│   ├── navigation.py        # Navigation related commands
│   ├── file_ops.py          # File operation commands
│   ├── system.py            # System information commands
│   └── utilities.py         # Utility & search commands
├── filesystem/              # Virtual file system layer
│   └── virtual_fs.py        # Core virtual file system logic
├── assets/                  # Static resource files
│   └── c_drive.json         # Initial C-drive structure data
└── tests/                   # Unit test directory
    ├── test_virtual_fs.py   # Virtual file system test cases
    └── test_commands.py     # Command function test cases
```

## Architecture Introduction

The project adopts a three-layer separation architecture:

1. **File System Layer** (`filesystem/`): VirtualFileSystem provides unified file operation interfaces
2. **Command Layer** (`commands/`): All functional commands inherit the base Command class to implement business logic
3. **Shell Layer** (`shells/`): CmdShell receives user input, parses and dispatches command execution

## Usage Demo

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

## Run Test Cases

```bash
# Run all test suites
python -m unittest discover -s tests -v

# Run single test file
python -m unittest tests.test_virtual_fs

# Run simple standalone test script
python test_simple.py
```

## Contact

TEL.: 18770020040

WECHAT: 18770020040

Thanks for using this project! If you have any questions or need further assistance, feel free to reach out. Happy coding! 🚀
