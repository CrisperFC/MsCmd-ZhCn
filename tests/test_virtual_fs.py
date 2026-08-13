"""
虚拟文件系统单元测试
"""

import unittest
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from filesystem.virtual_fs import VirtualFileSystem, VirtualFile, VirtualDirectory, create_virtual_fs


class TestVirtualFile(unittest.TestCase):
    """测试VirtualFile类"""
    
    def test_create_file(self):
        """测试创建文件"""
        vf = VirtualFile("test.txt", content="hello")
        self.assertEqual(vf.name, "test.txt")
        self.assertEqual(vf.content, "hello")
        self.assertEqual(vf.size, 5)
    
    def test_file_to_dict(self):
        """测试文件序列化"""
        vf = VirtualFile("test.txt", content="hello")
        d = vf.to_dict()
        self.assertEqual(d["type"], "file")
        self.assertEqual(d["name"], "test.txt")
        self.assertEqual(d["content"], "hello")
    
    def test_file_from_dict(self):
        """测试文件反序列化"""
        data = {"type": "file", "content": "test", "size": 4}
        vf = VirtualFile.from_dict("test.txt", data)
        self.assertEqual(vf.name, "test.txt")
        self.assertEqual(vf.content, "test")


class TestVirtualDirectory(unittest.TestCase):
    """测试VirtualDirectory类"""
    
    def test_create_directory(self):
        """测试创建目录"""
        vd = VirtualDirectory("test")
        self.assertEqual(vd.name, "test")
        self.assertEqual(len(vd.children), 0)
    
    def test_add_item(self):
        """测试添加项"""
        vd = VirtualDirectory("test")
        vf = VirtualFile("file.txt")
        vd.add(vf)
        self.assertEqual(len(vd.children), 1)
        self.assertTrue(vd.exists("file.txt"))
    
    def test_remove_item(self):
        """测试删除项"""
        vd = VirtualDirectory("test")
        vf = VirtualFile("file.txt")
        vd.add(vf)
        result = vd.remove("file.txt")
        self.assertTrue(result)
        self.assertFalse(vd.exists("file.txt"))
    
    def test_remove_nonexistent(self):
        """测试删除不存在的项"""
        vd = VirtualDirectory("test")
        result = vd.remove("nonexistent.txt")
        self.assertFalse(result)
    
    def test_list_files_and_dirs(self):
        """测试列出文件和目录"""
        vd = VirtualDirectory("test")
        vd.add(VirtualFile("file1.txt"))
        vd.add(VirtualFile("file2.txt"))
        vd.add(VirtualDirectory("subdir"))
        
        self.assertEqual(len(vd.list_files()), 2)
        self.assertEqual(len(vd.list_dirs()), 1)


class TestVirtualFileSystem(unittest.TestCase):
    """测试VirtualFileSystem类"""
    
    def setUp(self):
        """每个测试前的设置"""
        self.fs = create_virtual_fs()
        # 初始化环境变量
        self.fs._env = {}
    
    def test_initial_path(self):
        """测试初始路径"""
        self.assertEqual(self.fs.pwd(), "C:")
    
    def test_cd(self):
        """测试切换目录"""
        success, msg = self.fs.cd("Windows")
        self.assertTrue(success)
        self.assertEqual(self.fs.pwd(), "C:\\Windows")
        
        success, msg = self.fs.cd("System32")
        self.assertTrue(success)
        self.assertEqual(self.fs.pwd(), "C:\\Windows\\System32")
    
    def test_cd_absolute_path(self):
        """测试绝对路径切换"""
        self.fs.cd("Windows")
        success, msg = self.fs.cd("C:\\Users")
        self.assertTrue(success)
        self.assertEqual(self.fs.pwd(), "C:\\Users")
    
    def test_cd_nonexistent(self):
        """测试切换到不存在的路径"""
        success, msg = self.fs.cd("NonExistent")
        self.assertFalse(success)
    
    def test_cd_relative_path(self):
        """测试相对路径切换"""
        self.fs.cd("Windows")
        success, msg = self.fs.cd("..")
        self.assertTrue(success)
        self.assertEqual(self.fs.pwd(), "C:")
    
    def test_dir(self):
        """测试目录列表"""
        success, content = self.fs.dir()
        self.assertTrue(success)
        self.assertIn("Windows", content)
    
    def test_mkdir(self):
        """测试创建目录"""
        success, msg = self.fs.mkdir("test_dir")
        self.assertTrue(success)
        self.assertTrue(self.fs.path_exists("test_dir"))
    
    def test_mkdir_nested(self):
        """测试创建嵌套目录"""
        success, msg = self.fs.mkdir("parent\\child")
        self.assertTrue(success)
        self.assertTrue(self.fs.path_exists("parent\\child"))
    
    def test_touch(self):
        """测试创建文件"""
        success, msg = self.fs.touch("test.txt", content="hello")
        self.assertTrue(success)
        self.assertTrue(self.fs.path_exists("test.txt"))
    
    def test_read_write_file(self):
        """测试读写文件"""
        self.fs.touch("test.txt", content="hello world")
        success, content = self.fs.read_file("test.txt")
        self.assertTrue(success)
        self.assertEqual(content, "hello world")
    
    def test_delete(self):
        """测试删除文件"""
        self.fs.touch("test.txt")
        success, msg = self.fs.delete("test.txt")
        self.assertTrue(success)
        self.assertFalse(self.fs.path_exists("test.txt"))
    
    def test_rename(self):
        """测试重命名"""
        self.fs.touch("old.txt")
        success, msg = self.fs.rename("old.txt", "new.txt")
        self.assertTrue(success)
        self.assertFalse(self.fs.path_exists("old.txt"))
        self.assertTrue(self.fs.path_exists("new.txt"))
    
    def test_copy(self):
        """测试复制文件"""
        self.fs.touch("source.txt", content="copy me")
        success, msg = self.fs.copy("source.txt", "dest.txt")
        self.assertTrue(success)
        self.assertTrue(self.fs.path_exists("dest.txt"))
        
        success, content = self.fs.read_file("dest.txt")
        self.assertEqual(content, "copy me")
    
    def test_normalize_path(self):
        """测试路径规范化"""
        self.assertEqual(self.fs.normalize_path("C:/Users/./test/../Admin"), "C:\\Users\\Admin")
        self.assertEqual(self.fs.normalize_path("C:/Users///test"), "C:\\Users\\test")
    
    def test_glob_match(self):
        """测试通配符匹配"""
        self.assertTrue(self.fs.glob_match("*.txt", "test.txt"))
        self.assertFalse(self.fs.glob_match("*.txt", "test.doc"))
        self.assertTrue(self.fs.glob_match("test?", "test1"))
    
    def test_find_items_by_pattern(self):
        """测试模式匹配查找"""
        # 在Windows目录下查找.sys文件
        results = self.fs.find_items_by_pattern("C:\\Windows", "*.sys")
        self.assertTrue(len(results) >= 2)  # pagefile.sys, hiberfil.sys, swapfile.sys
    
    def test_rmdir_recursive(self):
        """测试递归删除"""
        self.fs.mkdir("test_dir\\sub1\\sub2")
        self.fs.touch("test_dir\\file1.txt")
        self.fs.touch("test_dir\\sub1\\file2.txt")
        
        success, msg = self.fs.rmdir_recursive("test_dir")
        self.assertTrue(success)
        self.assertFalse(self.fs.path_exists("test_dir"))
    
    def test_tree(self):
        """测试树形显示"""
        self.fs.mkdir("test_dir")
        self.fs.touch("test_dir\\file1.txt")
        self.fs.touch("test_dir\\file2.txt")
        self.fs.mkdir("test_dir\\subdir")
        
        success, content = self.fs.tree("test_dir")
        self.assertTrue(success)
        self.assertIn("file1.txt", content)
        self.assertIn("file2.txt", content)
        self.assertIn("subdir", content)
    
    def test_disk_usage(self):
        """测试磁盘使用"""
        self.fs.touch("test.txt", content="a" * 1000)
        success, content = self.fs.disk_usage("test.txt")
        self.assertTrue(success)
        self.assertIn("B", content)
    
    def test_write_file_append(self):
        """测试追加写入"""
        self.fs.touch("test.txt", content="line1\n")
        self.fs.write_file("test.txt", "line2\n", append=True)
        
        success, content = self.fs.read_file("test.txt")
        self.assertTrue(success)
        self.assertIn("line1", content)
        self.assertIn("line2", content)
    
    def test_path_resolution(self):
        """测试路径解析"""
        self.fs.cd("Windows")
        path = self.fs.resolve_path("..\\Users")
        self.assertEqual(path, ["C:", "Users"])


class TestVirtualFileSystemWithJSON(unittest.TestCase):
    """测试从JSON加载文件系统"""
    
    def test_load_from_json(self):
        """测试从JSON加载"""
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "c_drive.json")
        fs = VirtualFileSystem(json_path)
        
        self.assertTrue(fs.path_exists("Windows"))
        self.assertTrue(fs.path_exists("Users"))
        self.assertTrue(fs.path_exists("Program Files"))


if __name__ == '__main__':
    unittest.main()