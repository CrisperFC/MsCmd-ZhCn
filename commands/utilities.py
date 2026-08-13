"""
工具命令
color, title, prompt, set, tree, find, where, path, cls, setx
"""

from .base import Command


class TreeCommand(Command):
    """tree - 树形显示目录结构"""
    
    def get_name(self):
        return "tree"
    
    def get_description(self):
        return "显示目录结构树。"
    
    def execute(self, args):
        # 解析参数
        path = None
        show_files = False
        use_ascii = False
        
        for i, arg in enumerate(args):
            if arg.lower() == "/f":
                show_files = True
            elif arg.lower() == "/a":
                use_ascii = True
            elif not arg.startswith("/"):
                path = " ".join(args[i:])
                break
        
        success, content = self.fs.tree(path)
        if success:
            return True, content + "\n"
        return False, content


class FindCommand(Command):
    """find - 在文件中搜索字符串"""
    
    def get_name(self):
        return "find"
    
    def get_description(self):
        return "在文件中搜索特定的文字。"
    
    def execute(self, args):
        if not args:
            return False, "语法错误。\n\n用法: find [/i] [/n] [/v] \"字符串\" [文件]"
        
        # 解析参数
        case_sensitive = True
        show_line_numbers = False
        show_non_matching = False
        search_string = None
        file_path = None
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.lower() == "/i":
                case_sensitive = False
            elif arg.lower() == "/n":
                show_line_numbers = True
            elif arg.lower() == "/v":
                show_non_matching = True
            elif arg.startswith('"') and arg.endswith('"'):
                search_string = arg[1:-1]
            elif not search_string:
                search_string = arg
            elif not arg.startswith("/"):
                file_path = " ".join(args[i:])
                break
            i += 1
        
        if not search_string:
            return False, "未指定搜索字符串。"
        
        if not file_path:
            return False, "未指定搜索文件。"
        
        # 读取文件
        success, content = self.fs.read_file(file_path)
        if not success:
            return False, content
        
        # 搜索
        lines = content.split('\n')
        results = []
        
        search_str = search_string if case_sensitive else search_string.lower()
        
        for line_num, line in enumerate(lines, 1):
            line_to_check = line if case_sensitive else line.lower()
            is_match = search_str in line_to_check
            
            if (is_match and not show_non_matching) or (not is_match and show_non_matching):
                if show_line_numbers:
                    results.append(f"({line_num}){line}")
                else:
                    results.append(line)
        
        if not results:
            return True, "(未找到匹配项)\n"
        
        return True, "\n".join(results) + "\n"


class WhereCommand(Command):
    """where - 查找文件"""
    
    def get_name(self):
        return "where"
    
    def get_description(self):
        return "搜索并显示文件的位置。"
    
    def execute(self, args):
        if not args:
            return False, "语法错误。\n\n用法: where [/r dir] [pattern]"
        
        # 解析参数
        recursive = False
        search_dir = ""
        pattern = "*"
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.lower() == "/r" and i + 1 < len(args):
                recursive = True
                search_dir = args[i + 1]
                i += 2
            elif not arg.startswith("/"):
                pattern = arg
                break
            i += 1
        
        # 搜索
        if recursive and search_dir:
            results = self.fs.find_items_recursive(search_dir, pattern, include_files=True, include_dirs=False)
            lines = []
            for rel_path, item in results:
                full_path = f"{search_dir}\\{rel_path}" if search_dir else rel_path
                lines.append(full_path)
        else:
            results = self.fs.find_items_by_pattern(search_dir, pattern, include_files=True, include_dirs=True)
            lines = []
            for name, item in results:
                pwd = self.fs.pwd()
                lines.append(f"{pwd}\\{name}")
        
        if not lines:
            return False, "错误: 为指定模式未找到文件。\n"
        
        return True, "\n".join(lines) + "\n"


class PathCommand(Command):
    """path - 显示或设置PATH环境变量"""
    
    def get_name(self):
        return "path"
    
    def get_description(self):
        return "显示或设置可执行文件的搜索路径。"
    
    def execute(self, args):
        if not hasattr(self.fs, '_env'):
            self.fs._env = {}
        
        # 默认PATH
        default_path = "C:\\Windows\\system32;C:\\Windows"
        current_path = self.fs._env.get("PATH", default_path)
        
        if not args:
            return True, f"PATH={current_path}\n"
        
        # 设置新PATH
        new_path = " ".join(args)
        self.fs._env["PATH"] = new_path
        return True, ""


class SetxCommand(Command):
    """setx - 永久设置环境变量（模拟）"""
    
    def get_name(self):
        return "setx"
    
    def get_description(self):
        return "设置环境变量（在当前会话中永久生效）。"
    
    def execute(self, args):
        if len(args) < 2:
            return False, "语法错误。\n\n用法: setx <变量名> <值>"
        
        if not hasattr(self.fs, '_env'):
            self.fs._env = {}
        
        key = args[0]
        value = " ".join(args[1:])
        
        self.fs._env[key] = value
        return True, f"成功: 已将值设置为 {key}\n"


class ColorCommand(Command):
    """color - 设置颜色"""
    
    def get_name(self):
        return "color"
    
    def get_description(self):
        return "设置默认控制台前景和背景颜色。"
    
    def execute(self, args):
        if not args:
            return True, "当前颜色设置: 07\n"
        # ANSI颜色码不实际修改，仅提示
        return True, ""


class TitleCommand(Command):
    """title - 设置窗口标题"""
    
    def get_name(self):
        return "title"
    
    def get_description(self):
        return "设置窗口标题。"
    
    def execute(self, args):
        if not args:
            return True, "Windows PowerShell\n"
        title = " ".join(args)
        return True, f"\x1b]0;{title}\x07"  # ANSI设置标题


class PromptCommand(Command):
    """prompt - 设置命令提示符"""
    
    def get_name(self):
        return "prompt"
    
    def get_description(self):
        return "设置命令解释程序的命令提示符。"
    
    def execute(self, args):
        if not args:
            return True, "$P$G\n"
        prompt = " ".join(args)
        # 转换CMD提示符变量
        prompt = prompt.replace("$P", "").replace("$G", ">").replace("$T", "").replace("$D", "")
        if not prompt.endswith(">"):
            prompt += ">"
        return True, f"__PROMPT__{prompt}"


class SetCommand(Command):
    """set - 显示/设置环境变量"""
    
    def get_name(self):
        return "set"
    
    def get_description(self):
        return "显示、设置或删除环境变量。"
    
    def execute(self, args):
        if not hasattr(self.fs, '_env'):
            self.fs._env = {}
        
        if not args:
            # 显示所有变量
            lines = ["Environment variables:"]
            # 添加一些默认变量
            defaults = {
                "PATH": "C:\\Windows\\system32;C:\\Windows",
                "TEMP": "C:\\Users\\Administrator\\AppData\\Local\\Temp",
                "TMP": "C:\\Users\\Administrator\\AppData\\Local\\Temp",
                "USERPROFILE": "C:\\Users\\Administrator",
                "SYSTEMROOT": "C:\\Windows",
                "COMPUTERNAME": "SIMULATED-PC",
                "USERNAME": "Administrator",
                "OS": "Windows_NT",
                "HOMEDRIVE": "C:",
                "HOMEPATH": "\\Users\\Administrator",
            }
            for key in sorted(defaults):
                lines.append(f"{key}={defaults[key]}")
            for key, value in sorted(self.fs._env.items()):
                lines.append(f"{key}={value}")
            return True, "\n".join(lines) + "\n"
        
        # 设置变量
        arg = args[0]
        if "=" in arg:
            key, value = arg.split("=", 1)
            self.fs._env[key] = value
            return True, ""
        
        # 查询变量
        for key, value in self.fs._env.items():
            if key.lower() == arg.lower():
                return True, f"{key}={value}\n"
        
        return True, ""


def register_commands(filesystem):
    """注册所有工具命令"""
    return [
        TreeCommand(filesystem),
        FindCommand(filesystem),
        WhereCommand(filesystem),
        PathCommand(filesystem),
        SetxCommand(filesystem),
        ColorCommand(filesystem),
        TitleCommand(filesystem),
        PromptCommand(filesystem),
        SetCommand(filesystem),
    ]