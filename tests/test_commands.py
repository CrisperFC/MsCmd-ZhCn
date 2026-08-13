"""
命令单元测试
"""

import unittest
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shells.cmd_shell import CmdShell


class TestCmdShell(unittest.TestCase):
    """测试CmdShell类"""
    
    def setUp(self):
        """每个测试前的设置"""
        self.shell = CmdShell()
    
    def test_command_registration(self):
        """测试命令注册"""
        self.assertGreater(len(self.shell.commands), 0)
        self.assertIn("cd", self.shell.commands)
        self.assertIn("dir", self.shell.commands)
        self.assertIn("copy", self.shell.commands)
    
    def test_cd_command(self):
        """测试cd命令"""
        success, output = self.shell.execute_command("cd Windows")
        self.assertTrue(success)
    
    def test_dir_command(self):
        """测试dir命令"""
        success, output = self.shell.execute_command("dir")
        self.assertTrue(success)
        self.assertIn("Windows", output)
    
    def test_ver_command(self):
        """测试ver命令"""
        success, output = self.shell.execute_command("ver")
        self.assertTrue(success)
        self.assertIn("Windows", output)
    
    def test_help_command(self):
        """测试help命令"""
        success, output = self.shell.execute_command("help")
        self.assertTrue(success)
        self.assertIn("CD", output)
    
    def test_mkdir_command(self):
        """测试mkdir命令"""
        success, output = self.shell.execute_command("mkdir test_dir")
        self.assertTrue(success)
    
    def test_echo_command(self):
        """测试echo命令"""
        success, output = self.shell.execute_command("echo hello")
        self.assertTrue(success)
        self.assertIn("hello", output)
    
    def test_tree_command(self):
        """测试tree命令"""
        success, output = self.shell.execute_command("tree C:\\Windows")
        self.assertTrue(success)
        self.assertIn("System32", output)
    
    def test_where_command(self):
        """测试where命令"""
        success, output = self.shell.execute_command("where *.sys")
        self.assertTrue(success)
    
    def test_set_command(self):
        """测试set命令"""
        success, output = self.shell.execute_command("set TEST=123")
        self.assertTrue(success)
        
        success, output = self.shell.execute_command("set TEST")
        self.assertIn("123", output)
    
    def test_path_command(self):
        """测试path命令"""
        success, output = self.shell.execute_command("path")
        self.assertTrue(success)
        self.assertIn("PATH=", output)
    
    def test_unknown_command(self):
        """测试未知命令"""
        success, output = self.shell.execute_command("unknown_command")
        self.assertFalse(success)
    
    def test_and_operator(self):
        """测试&&操作符"""
        success, output = self.shell.execute_command("cd Windows && dir")
        self.assertTrue(success)
    
    def test_or_operator(self):
        """测试||操作符"""
        success, output = self.shell.execute_command("unknown_cmd || echo fallback")
        # 第一个命令失败，执行第二个
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()