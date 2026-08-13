"""
虚拟文件系统模块
模拟Windows C盘文件系统结构
"""

import json
import os
import sys
import time
import copy
import fnmatch
import logging
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)


class VirtualFile:
    """虚拟文件"""
    
    def __init__(self, name, content="", size=None):
        self.name = name
        self.content = content
        self.size = size if size is not None else len(content.encode('utf-8', errors='replace'))
        self.created_time = datetime.now()
        self.modified_time = datetime.now()
    
    def to_dict(self):
        return {
            "type": "file",
            "name": self.name,
            "size": self.size,
            "content": self.content if self.content else None,
            "created": self.created_time.isoformat(),
            "modified": self.modified_time.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, name, data):
        vf = cls(name, content=data.get("content", ""), size=data.get("size"))
        if data.get("created"):
            vf.created_time = datetime.fromisoformat(data["created"])
        if data.get("modified"):
            vf.modified_time = datetime.fromisoformat(data["modified"])
        return vf


class VirtualDirectory:
    """虚拟目录"""
    
    def __init__(self, name):
        self.name = name
        self.children = {}  # name -> VirtualFile or VirtualDirectory
        self.created_time = datetime.now()
        self.modified_time = datetime.now()
    
    def add(self, item):
        self.children[item.name] = item
        self.modified_time = datetime.now()
    
    def remove(self, name):
        if name in self.children:
            del self.children[name]
            self.modified_time = datetime.now()
            return True
        return False
    
    def get(self, name):
        return self.children.get(name)
    
    def exists(self, name):
        return name in self.children
    
    def list_files(self):
        return [child for child in self.children.values() if isinstance(child, VirtualFile)]
    
    def list_dirs(self):
        return [child for child in self.children.values() if isinstance(child, VirtualDirectory)]
    
    def to_dict(self):
        result = {
            "type": "dir",
            "name": self.name,
            "children": {},
            "created": self.created_time.isoformat(),
            "modified": self.modified_time.isoformat(),
        }
        for name, child in self.children.items():
            result["children"][name] = child.to_dict()
        return result


class VirtualFileSystem:
    """虚拟文件系统"""
    
    def __init__(self, data_path=None):
        self.root = VirtualDirectory("C:")
        self.current_path = ["C:"]  # 当前路径栈
        if data_path and os.path.exists(data_path):
            self._load_from_json(data_path)
    
    def _load_from_json(self, path):
        """从JSON加载虚拟文件系统"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 获取C:的数据
        c_drive_data = data.get("C:", data)
        self._build_from_dict(c_drive_data, self.root)
    
    def _build_from_dict(self, data, parent):
        """递归构建文件系统"""
        if "children" in data:
            for name, child_data in data["children"].items():
                if child_data.get("type") == "dir":
                    vdir = VirtualDirectory(name)
                    self._build_from_dict(child_data, vdir)
                    parent.add(vdir)
                else:
                    vfile = VirtualFile.from_dict(name, child_data)
                    parent.add(vfile)
    
    def get_current_dir(self):
        """获取当前目录对象"""
        current = self.root
        for part in self.current_path[1:]:
            if isinstance(current, VirtualDirectory):
                child = current.get(part)
                if isinstance(child, VirtualDirectory):
                    current = child
                else:
                    return None
            else:
                return None
        return current
    
    def resolve_path(self, path_str):
        """解析路径字符串为路径列表"""
        if not path_str:
            return self.current_path.copy()
        
        # 处理绝对路径
        if path_str.startswith("C:") or path_str.startswith("C:/") or path_str.startswith("C:\\"):
            parts = ["C:"]
            path_str = path_str[2:].lstrip("\\").lstrip("/")
        elif path_str.startswith("/") or path_str.startswith("\\"):
            parts = ["C:"]
            path_str = path_str.lstrip("\\").lstrip("/")
        else:
            # 相对路径
            parts = self.current_path.copy()
        
        if path_str:
            for part in path_str.replace("\\", "/").split("/"):
                if part and part != ".":
                    parts.append(part)
                elif part == "..":
                    if len(parts) > 1:
                        parts.pop()
        
        return parts
    
    def get_dir_by_path(self, path_list):
        """根据路径列表获取目录对象"""
        current = self.root
        for part in path_list[1:]:
            if isinstance(current, VirtualDirectory):
                child = current.get(part)
                if isinstance(child, VirtualDirectory):
                    current = child
                else:
                    return None
            else:
                return None
        return current
    
    def get_item_by_path(self, path_list):
        """根据路径列表获取任意项"""
        current = self.root
        for part in path_list[1:]:
            if isinstance(current, VirtualDirectory):
                child = current.get(part)
                if child:
                    current = child
                else:
                    return None
            else:
                return None
        return current
    
    def cd(self, path_str):
        """切换目录"""
        path_list = self.resolve_path(path_str)
        target = self.get_dir_by_path(path_list)
        if target is not None:
            self.current_path = path_list
            return True, ""
        return False, f"系统找不到指定的路径。"
    
    def pwd(self):
        """获取当前工作目录"""
        return "\\".join(self.current_path).replace("C:", "C:")
    
    def dir(self, path_str=None, show_hidden=False):
        """列出目录内容"""
        target_path = self.resolve_path(path_str) if path_str else self.current_path
        target = self.get_dir_by_path(target_path)
        
        if target is None:
            return False, f"系统找不到指定的路径。"
        
        if not isinstance(target, VirtualDirectory):
            # 显示单个文件信息
            return False, f"系统找不到指定的文件。"
        
        lines = []
        dirs = []
        files = []
        
        for name, child in target.children.items():
            if isinstance(child, VirtualDirectory):
                dirs.append(child)
            else:
                files.append(child)
        
        # 目录部分
        for d in dirs:
            size_str = "<DIR>"
            lines.append(f" {d.modified_time.strftime('%Y-%m-%d  %H:%M')}    {size_str} {d.name}")
        
        # 文件部分
        for f in files:
            size_str = f"{f.size:>15}" if f.size > 0 else "               0"
            lines.append(f" {f.modified_time.strftime('%Y-%m-%d  %H:%M')}    {size_str} {f.name}")
        
        # 统计
        total_dirs = len(dirs)
        total_files = len(files)
        lines.append(f"               {total_files} File(s)")
        lines.append(f"               {total_dirs} Dir(s)")
        
        return True, "\n".join(lines)
    
    def mkdir(self, path_str):
        """创建目录（支持 -p 参数创建嵌套目录）"""
        path_list = self.resolve_path(path_str)
        
        # 尝试逐级创建目录
        current_path = ["C:"]
        for i, part in enumerate(path_list[1:], 1):
            current_path.append(part)
            current_item = self.get_item_by_path(current_path)
            
            if current_item is None:
                # 目录不存在，创建
                parent = self.get_dir_by_path(current_path[:-1])
                if parent is None:
                    return False, f"系统找不到指定的路径。"
                parent.add(VirtualDirectory(part))
            elif not isinstance(current_item, VirtualDirectory):
                return False, f"文件已存在。"
        
        return True, ""
    
    def rmdir(self, path_str):
        """删除空目录"""
        path_list = self.resolve_path(path_str)
        parent_path = path_list[:-1]
        dir_name = path_list[-1]
        
        parent = self.get_dir_by_path(parent_path)
        if parent is None:
            return False, f"系统找不到指定的路径。"
        
        target = parent.get(dir_name)
        if target is None:
            return False, f"系统找不到指定的路径。"
        
        if not isinstance(target, VirtualDirectory):
            return False, f"目录不是目录。"
        
        if target.children:
            return False, f"目录不是空的。"
        
        parent.remove(dir_name)
        return True, ""
    
    def touch(self, path_str, content=""):
        """创建文件"""
        path_list = self.resolve_path(path_str)
        parent_path = path_list[:-1]
        file_name = path_list[-1]
        
        if not file_name:
            return False, "语法错误。"
        
        parent = self.get_dir_by_path(parent_path)
        if parent is None:
            return False, f"系统找不到指定的路径。"
        
        parent.add(VirtualFile(file_name, content=content))
        return True, ""
    
    def read_file(self, path_str):
        """读取文件内容"""
        path_list = self.resolve_path(path_str)
        target = self.get_item_by_path(path_list)
        
        if target is None:
            return False, f"系统找不到指定的文件。"
        
        if isinstance(target, VirtualDirectory):
            return False, f"指定的路径是目录。"
        
        return True, target.content
    
    def write_file(self, path_str, content, append=False):
        """写入文件内容"""
        path_list = self.resolve_path(path_str)
        target = self.get_item_by_path(path_list)
        
        if target is not None and isinstance(target, VirtualDirectory):
            return False, f"指定的路径是目录。"
        
        if target is not None and isinstance(target, VirtualFile):
            if append:
                target.content += content
            else:
                target.content = content
            target.size = len(target.content.encode('utf-8', errors='replace'))
            target.modified_time = datetime.now()
            return True, ""
        
        # 文件不存在，需要创建
        parent_path = path_list[:-1]
        file_name = path_list[-1]
        parent = self.get_dir_by_path(parent_path)
        
        if parent is None:
            return False, f"系统找不到指定的路径。"
        
        parent.add(VirtualFile(file_name, content=content))
        return True, ""
    
    def delete(self, path_str):
        """删除文件"""
        path_list = self.resolve_path(path_str)
        parent_path = path_list[:-1]
        item_name = path_list[-1]
        
        parent = self.get_dir_by_path(parent_path)
        if parent is None:
            return False, f"系统找不到指定的路径。"
        
        target = parent.get(item_name)
        if target is None:
            return False, f"系统找不到指定的文件。"
        
        if isinstance(target, VirtualDirectory):
            return False, f"无法删除目录。请使用 rmdir。"
        
        parent.remove(item_name)
        return True, ""
    
    def rename(self, old_path_str, new_name):
        """重命名文件/目录"""
        path_list = self.resolve_path(old_path_str)
        parent_path = path_list[:-1]
        old_name = path_list[-1]
        
        parent = self.get_dir_by_path(parent_path)
        if parent is None:
            return False, f"系统找不到指定的路径。"
        
        if not parent.exists(old_name):
            return False, f"系统找不到指定的文件。"
        
        if parent.exists(new_name):
            return False, f"文件已存在。"
        
        item = parent.get(old_name)
        parent.remove(old_name)
        item.name = new_name
        parent.add(item)
        return True, ""
    
    def copy(self, src_path_str, dst_path_str):
        """复制文件"""
        src = self.get_item_by_path(self.resolve_path(src_path_str))
        if src is None:
            return False, f"系统找不到指定的文件。"
        
        if isinstance(src, VirtualDirectory):
            return False, f"无法复制目录。"
        
        # 解析目标路径
        dst_path_list = self.resolve_path(dst_path_str)
        dst_parent = self.get_dir_by_path(dst_path_list[:-1])
        
        if dst_parent is None:
            return False, f"系统找不到指定的路径。"
        
        dst_name = dst_path_list[-1]
        new_file = VirtualFile(dst_name, content=src.content, size=src.size)
        dst_parent.add(new_file)
        return True, ""
    
    def normalize_path(self, path_str):
        """
        路径规范化：处理 . 和 ..，统一分隔符，去除多余分隔符
        """
        if not path_str:
            return ""
        
        # 统一使用反斜杠（Windows 风格）
        path_str = path_str.replace("/", "\\")
        
        # 去除连续的反斜杠
        while "\\\\" in path_str:
            path_str = path_str.replace("\\\\", "\\")
        
        # 处理 drive letter
        drive = ""
        if len(path_str) >= 2 and path_str[1] == ':':
            drive = path_str[:2]
            path_str = path_str[2:]
        
        # 去除前导反斜杠用于处理
        is_absolute = path_str.startswith("\\")
        path_str = path_str.lstrip("\\")
        
        parts = []
        for part in path_str.split("\\"):
            if part == "" or part == ".":
                continue
            elif part == "..":
                if parts and parts[-1] != "..":
                    parts.pop()
                elif is_absolute or drive:
                    # 绝对路径不能超出根
                    pass
                else:
                    # 相对路径可以超出当前目录
                    parts.append("..")
            else:
                parts.append(part)
        
        result = drive
        if is_absolute or drive:
            result += "\\"
        result += "\\".join(parts)
        
        return result if result else drive
    
    def resolve_path(self, path_str):
        """解析路径字符串为路径列表（增强版：支持路径规范化）"""
        if not path_str:
            return self.current_path.copy()
        
        # 检查是否是绝对路径
        is_absolute = (path_str.startswith("C:") or path_str.startswith("C:/") or 
                       path_str.startswith("C:\\") or path_str.startswith("/") or path_str.startswith("\\"))
        
        if is_absolute:
            # 绝对路径：从根开始
            parts = ["C:"]
            # 移除 drive letter 和前导分隔符
            if path_str.startswith("C:") or path_str.startswith("C:/") or path_str.startswith("C:\\"):
                path_str = path_str[2:]
            path_str = path_str.lstrip("/").lstrip("\\")
        else:
            # 相对路径：从当前路径开始
            parts = self.current_path.copy()
        
        # 统一使用反斜杠
        path_str = path_str.replace("/", "\\")
        
        # 处理路径部分
        for part in path_str.split("\\"):
            if not part or part == ".":
                continue
            elif part == "..":
                if len(parts) > 1:
                    parts.pop()
            else:
                parts.append(part)
        
        return parts
    
    def glob_match(self, pattern, name):
        """
        通配符匹配：支持 * 和 ?
        * 匹配任意字符序列（不包含反斜杠）
        ? 匹配单个字符
        """
        return fnmatch.fnmatchcase(name.lower(), pattern.lower())
    
    def find_items_by_pattern(self, dir_path_str, pattern, include_files=True, include_dirs=True):
        """
        在指定目录中查找匹配通配符模式的文件和目录
        返回匹配项列表: [(name, item), ...]
        """
        target = self.get_dir_by_path(self.resolve_path(dir_path_str) if dir_path_str else self.current_path)
        if target is None:
            return []
        
        results = []
        for name, item in target.children.items():
            is_file = isinstance(item, VirtualFile)
            is_dir = isinstance(item, VirtualDirectory)
            
            if (include_files and is_file) or (include_dirs and is_dir):
                if self.glob_match(pattern, name):
                    results.append((name, item))
        
        return results
    
    def find_items_recursive(self, dir_path_str, pattern, include_files=True, include_dirs=False):
        """
        递归查找匹配通配符模式的文件
        返回匹配项列表: [(relative_path, item), ...]
        """
        target = self.get_dir_by_path(self.resolve_path(dir_path_str) if dir_path_str else self.current_path)
        if target is None:
            return []
        
        return self._recursive_search(target, "", pattern, include_files, include_dirs)
    
    def _recursive_search(self, directory, relative_path, pattern, include_files, include_dirs):
        """递归搜索内部方法"""
        results = []
        for name, item in directory.children.items():
            current_path = f"{relative_path}\\{name}" if relative_path else name
            
            if isinstance(item, VirtualFile) and include_files:
                if self.glob_match(pattern, name):
                    results.append((current_path, item))
            elif isinstance(item, VirtualDirectory):
                if include_dirs and self.glob_match(pattern, name):
                    results.append((current_path, item))
                # 递归搜索子目录
                results.extend(self._recursive_search(item, current_path, pattern, include_files, include_dirs))
        
        return results
    
    def rmdir_recursive(self, path_str):
        """
        递归删除目录及其所有内容
        对应 CMD 的 rmdir /s
        """
        path_list = self.resolve_path(path_str)
        parent_path = path_list[:-1]
        dir_name = path_list[-1]
        
        parent = self.get_dir_by_path(parent_path)
        if parent is None:
            return False, f"系统找不到指定的路径。"
        
        target = parent.get(dir_name)
        if target is None:
            return False, f"系统找不到指定的路径。"
        
        if not isinstance(target, VirtualDirectory):
            return False, f"指定的路径是文件，不是目录。"
        
        # 递归删除
        self._remove_recursive(target)
        parent.remove(dir_name)
        logger.info(f"递归删除目录: {path_str}")
        return True, ""
    
    def _remove_recursive(self, directory):
        """递归删除目录中的所有项"""
        names = list(directory.children.keys())
        for name in names:
            item = directory.get(name)
            if isinstance(item, VirtualDirectory):
                self._remove_recursive(item)
            directory.remove(name)
    
    def tree(self, path_str=None, depth=None, current_depth=0):
        """
        以树形结构显示目录内容
        对应 CMD 的 tree 命令
        """
        target = self.get_dir_by_path(self.resolve_path(path_str) if path_str else self.current_path)
        if target is None:
            return False, f"系统找不到指定的路径。"
        
        if not isinstance(target, VirtualDirectory):
            return False, f"指定的路径是文件，不是目录。"
        
        lines = []
        pwd = self.pwd() if not path_str else path_str
        lines.append(f"  {pwd}")
        lines.append("  <DIR> " + target.name)
        lines.append("")
        self._tree_recursive(target, lines, "", depth, current_depth)
        
        # 统计
        total_dirs = self._count_dirs(target)
        total_files = self._count_files(target)
        lines.append(f"               {total_files} File(s)")
        lines.append(f"               {total_dirs} Dir(s)")
        
        return True, "\n".join(lines)
    
    def _tree_recursive(self, directory, lines, prefix, max_depth, current_depth):
        """递归生成树形输出"""
        if max_depth is not None and current_depth >= max_depth:
            return
        
        items = list(directory.children.items())
        for i, (name, item) in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "
            
            if isinstance(item, VirtualDirectory):
                lines.append(f"{prefix}{connector}<DIR> {name}")
                self._tree_recursive(item, lines, prefix + extension, max_depth, current_depth + 1)
            else:
                size_str = f"{item.size:>10}" if item.size > 0 else "         0"
                lines.append(f"{prefix}{connector}{name:<30} {size_str}")
    
    def _count_dirs(self, directory):
        """统计目录数量"""
        count = 0
        for item in directory.children.values():
            if isinstance(item, VirtualDirectory):
                count += 1
                count += self._count_dirs(item)
        return count
    
    def _count_files(self, directory):
        """统计文件数量"""
        count = 0
        for item in directory.children.values():
            if isinstance(item, VirtualFile):
                count += 1
            elif isinstance(item, VirtualDirectory):
                count += self._count_files(item)
        return count
    
    def disk_usage(self, path_str=None):
        """
        计算指定路径的磁盘使用情况
        """
        target = self.get_item_by_path(self.resolve_path(path_str) if path_str else self.current_path)
        if target is None:
            return False, f"系统找不到指定的路径。"
        
        if isinstance(target, VirtualFile):
            return True, self._format_size(target.size)
        
        if isinstance(target, VirtualDirectory):
            total = self._calculate_size(target)
            return True, self._format_size(total)
        
        return False, "无法计算大小。"
    
    def _calculate_size(self, item):
        """递归计算大小"""
        if isinstance(item, VirtualFile):
            return item.size
        elif isinstance(item, VirtualDirectory):
            return sum(self._calculate_size(child) for child in item.children.values())
        return 0
    
    def _format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    
    def path_exists(self, path_str):
        """检查路径是否存在"""
        path_list = self.resolve_path(path_str)
        return self.get_item_by_path(path_list) is not None


def get_resource_path(relative_path):
    """获取资源文件路径，兼容PyInstaller打包"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的路径
        base_path = sys._MEIPASS
    else:
        # 正常Python环境
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def create_virtual_fs():
    """创建虚拟文件系统实例"""
    data_path = get_resource_path(os.path.join("assets", "c_drive.json"))
    return VirtualFileSystem(data_path)