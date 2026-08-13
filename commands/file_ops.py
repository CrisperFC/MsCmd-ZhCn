"""
文件操作命令
copy, del, ren, type, mkdir, rmdir, echo, more
"""

from .base import Command


class CopyCommand(Command):
    """copy - 复制文件"""
    
    def get_name(self):
        return "copy"
    
    def get_description(self):
        return "将一个或多个文件复制到另一个位置。"
    
    def execute(self, args):
        if len(args) < 2:
            return False, "语法错误。\n\n用法: copy <源文件> <目标文件>"
        
        src = args[0]
        dst = args[1]
        success, msg = self.fs.copy(src, dst)
        if success:
            return True, f"        1 file(s) copied.\n"
        return False, msg


class DelCommand(Command):
    """del - 删除文件"""
    
    def get_name(self):
        return "del"
    
    def get_description(self):
        return "删除一个或多个文件。"
    
    def execute(self, args):
        if not args:
            return False, "语法错误。\n\n用法: del <文件>"
        
        # 处理 /q /f 等参数
        file_args = [a for a in args if not a.startswith("/")]
        if not file_args:
            return False, "语法错误。"
        
        results = []
        for f in file_args:
            success, msg = self.fs.delete(f)
            if not success:
                results.append(msg)
        
        if results:
            return False, "\n".join(results)
        return True, ""


class RenCommand(Command):
    """ren - 重命名文件"""
    
    def get_name(self):
        return "ren"
    
    def get_alias(self):
        return "rename"
    
    def get_description(self):
        return "重命名文件。"
    
    def execute(self, args):
        if len(args) < 2:
            return False, "语法错误。\n\n用法: ren <旧文件名> <新文件名>"
        
        old_path = args[0]
        new_name = args[1]
        success, msg = self.fs.rename(old_path, new_name)
        if success:
            return True, ""
        return False, msg


class TypeCommand(Command):
    """type - 显示文件内容"""
    
    def get_name(self):
        return "type"
    
    def get_description(self):
        return "显示文本文件的内容。"
    
    def execute(self, args):
        if not args:
            return False, "语法错误。\n\n用法: type <文件>"
        
        path = args[0]
        success, content = self.fs.read_file(path)
        if success:
            return True, content
        return False, content


class MkdirCommand(Command):
    """mkdir - 创建目录"""
    
    def get_name(self):
        return "mkdir"
    
    def get_alias(self):
        return "md"
    
    def get_description(self):
        return "创建一个目录。"
    
    def execute(self, args):
        if not args:
            return False, "语法错误。\n\n用法: mkdir <目录>"
        
        path = args[0]
        success, msg = self.fs.mkdir(path)
        if success:
            return True, ""
        return False, msg


class RmdirCommand(Command):
    """rmdir - 删除目录"""
    
    def get_name(self):
        return "rmdir"
    
    def get_alias(self):
        return "rd"
    
    def get_description(self):
        return "删除一个目录。"
    
    def execute(self, args):
        if not args:
            return False, "语法错误。\n\n用法: rmdir [选项] <目录>"
        
        # 处理 /s /q 参数
        dir_args = [a for a in args if not a.startswith("/")]
        if not dir_args:
            return False, "语法错误。"
        
        path = dir_args[0]
        success, msg = self.fs.rmdir(path)
        if success:
            return True, ""
        return False, msg


class EchoCommand(Command):
    """echo - 显示消息或开关回显"""
    
    def get_name(self):
        return "echo"
    
    def get_description(self):
        return "显示消息，或把命令回显打开或关上。"
    
    def execute(self, args):
        if not args:
            return True, "ECHO is on.\n"
        
        if args[0].lower() == "off":
            return True, ""  # 实际应由shell处理回显状态
        if args[0].lower() == "on":
            return True, ""
        
        # 处理重定向 > 和 >>
        text = " ".join(args)
        redirect = None
        append = False
        
        for i, token in enumerate(args):
            if token in (">", ">>"):
                if i + 1 < len(args):
                    redirect = args[i + 1]
                    append = (token == ">>")
                    text = " ".join(args[:i])
                    break
        
        if redirect:
            success, msg = self.fs.write_file(redirect, text + "\n", append=append)
            if success:
                return True, ""
            return False, msg
        
        return True, text + "\n"


class MoreCommand(Command):
    """more - 逐页显示"""
    
    def get_name(self):
        return "more"
    
    def get_description(self):
        return "逐屏显示输出。"
    
    def execute(self, args):
        if not args:
            return False, "语法错误。\n\n用法: more <文件>"
        
        path = args[0]
        success, content = self.fs.read_file(path)
        if success:
            return True, content + "\n"
        return False, content


def register_commands(filesystem):
    """注册所有文件操作命令"""
    return [
        CopyCommand(filesystem),
        DelCommand(filesystem),
        RenCommand(filesystem),
        TypeCommand(filesystem),
        MkdirCommand(filesystem),
        RmdirCommand(filesystem),
        EchoCommand(filesystem),
        MoreCommand(filesystem),
    ]