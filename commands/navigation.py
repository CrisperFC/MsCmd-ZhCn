"""
导航命令
cd, dir, pwd
"""

from .base import Command


class CdCommand(Command):
    """cd - 切换目录"""
    
    def get_name(self):
        return "cd"
    
    def get_description(self):
        return "显示当前目录的名称或将其更改。"
    
    def execute(self, args):
        if not args:
            return True, self.fs.pwd()
        
        path = args[0]
        # 处理 /d 参数
        if path == "/d" and len(args) > 1:
            path = args[1]
        
        success, msg = self.fs.cd(path)
        if success:
            return True, ""
        return False, msg


class DirCommand(Command):
    """dir - 列出目录内容"""
    
    def get_name(self):
        return "dir"
    
    def get_description(self):
        return "显示一个目录中的文件和子目录。"
    
    def execute(self, args):
        path = None
        if args:
            # 处理 /a /w /o 等参数
            for i, arg in enumerate(args):
                if not arg.startswith("/"):
                    path = " ".join(args[i:])
                    break
        
        success, content = self.fs.dir(path)
        if success:
            pwd = self.fs.pwd()
            header = f"\n {pwd}\n\n"
            return True, header + content + "\n"
        return False, content


class PwdCommand(Command):
    """pwd - 显示当前目录"""
    
    def get_name(self):
        return "pwd"
    
    def get_description(self):
        return "显示当前工作目录的完整路径。"
    
    def execute(self, args):
        return True, self.fs.pwd()


def register_commands(filesystem):
    """注册所有导航命令"""
    return [
        CdCommand(filesystem),
        DirCommand(filesystem),
        PwdCommand(filesystem),
    ]