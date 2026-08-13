"""
Windows CMD 模拟器
主入口文件
"""

# Import all modules from assets folder
import assets

# Import all modules from commands folder
import commands
from commands import base
from commands import file_ops
from commands import navigation
from commands import system
from commands import utilities

# Import all modules from filesystem folder
import filesystem
from filesystem import virtual_fs

# Import all modules from shells folder
import shells
from shells import cmd_shell

# Import all modules from tests folder
import tests
from tests import test_commands
from tests import test_virtual_fs

from shells.cmd_shell import main
import os

if __name__ == "__main__":
    os.startfile("setup.py")
    main()