"""
CMD Shell
主交互界面
"""

import sys
import os
import logging

# readline在Windows上可能不可用
try:
    import readline  # 命令行历史支持
    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False
    try:
        import pyreadline3 as readline  # Windows上的readline替代
        HAS_READLINE = True
    except ImportError:
        HAS_READLINE = False

# 配置日志
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from filesystem.virtual_fs import create_virtual_fs
from commands.navigation import register_commands as register_nav
from commands.file_ops import register_commands as register_file_ops
from commands.system import register_commands as register_system
from commands.utilities import register_commands as register_utilities


class CmdShell:
    """CMD命令行Shell"""
    
    def __init__(self, enable_logging=False):
        self.fs = create_virtual_fs()
        self.fs._env = {}
        self._setup_commands()
        self.prompt = "C:\\>"
        self.running = True
        self.echo_on = True
        self.history = []  # 命令历史
        self.history_max = 50  # 最大历史记录数
        
        if enable_logging:
            logger.setLevel(logging.DEBUG)
    
    def _setup_commands(self):
        """注册所有命令"""
        self.commands = {}
        self.command_list = []
        
        all_commands = (
            register_nav(self.fs) +
            register_file_ops(self.fs) +
            register_system(self.fs) +
            register_utilities(self.fs)
        )
        
        for cmd in all_commands:
            name = cmd.get_name().lower()
            self.commands[name] = cmd
            self.command_list.append(cmd)
            
            # 注册别名
            if hasattr(cmd, 'get_alias'):
                alias = cmd.get_alias()
                if alias:
                    self.commands[alias.lower()] = cmd
        
        self.fs._commands = self.command_list
    
    def _get_prompt(self):
        """获取当前提示符"""
        pwd = self.fs.pwd()
        return f"{pwd}> "
    
    def _print_banner(self):
        """打印启动横幅"""
        print("Microsoft Windows [版本 10.0.19045.3693]")
        print("(c) Microsoft Corporation。保留所有权利。")
        print()
    
    def _add_to_history(self, line):
        """添加命令到历史记录"""
        line = line.strip()
        if line and (not self.history or line != self.history[-1]):
            self.history.append(line)
            if len(self.history) > self.history_max:
                self.history.pop(0)
    
    def _process_pipe(self, line):
        """处理管道符 |"""
        parts = line.split("|")
        if len(parts) < 2:
            return None
        return parts
    
    def _process_redirect(self, line):
        """处理重定向 > 和 >>"""
        redirect_type = None
        redirect_file = None
        
        for i, token in enumerate(line.split()):
            if token in (">", ">>"):
                if i + 1 < len(line.split()):
                    redirect_type = token
                    redirect_file = line.split()[i + 1]
                    cmd_part = " ".join(line.split()[:i])
                    return cmd_part, redirect_type, redirect_file
        
        return line, None, None
    
    def run(self):
        """运行Shell"""
        self._print_banner()
        
        # 设置命令行历史
        try:
            if HAS_READLINE:
                readline.set_history_length(self.history_max)
        except Exception:
            pass  # readline可能不可用
        
        while self.running:
            try:
                line = input(self._get_prompt())
                self._add_to_history(line)
            except (EOFError, KeyboardInterrupt):
                print()
                self.running = False
                continue
            except Exception as e:
                print(f"错误: {e}")
                logger.error(f"输入错误: {e}")
                continue
            
            if not line.strip():
                continue
            
            # 处理退出
            if line.strip().lower() == "exit":
                self.running = False
                continue
            
            # 执行命令
            success, output = self.execute_command(line.strip())
            
            if output == "__EXIT__":
                self.running = False
                continue
            
            if output:
                # 检查是否需要处理清屏
                if output.startswith("\x1b[2J"):
                    # 清屏操作
                    try:
                        os.system('cls' if sys.platform == 'win32' else 'clear')
                    except Exception:
                        print("\n" * 50)
                    continue
                
                # 检查是否设置标题
                if "\x1b]0;" in output:
                    try:
                        title = output.split("\x1b]0;")[1].split("\x07")[0]
                        print(f"\x1b]0;{title}\x07", end="", flush=True)
                    except Exception:
                        pass
                    continue
                
                # 检查是否设置提示符
                if output.startswith("__PROMPT__"):
                    self.prompt = output[len("__PROMPT__"):]
                    continue
                
                print(output, end="" if output.endswith("\n") else "\n")
    
    def execute_command(self, line):
        """执行单行命令"""
        # 处理 && 和 ||
        if "&&" in line:
            parts = line.split("&&")
            outputs = []
            for part in parts:
                success, output = self.execute_command(part.strip())
                if not success:
                    return False, output
                if output:
                    outputs.append(output)
            return True, "\n".join(outputs) if outputs else ""
        
        if "||" in line:
            parts = line.split("||")
            outputs = []
            for i, part in enumerate(parts):
                success, output = self.execute_command(part.strip())
                if success:
                    return True, output
                if output:
                    outputs.append(output)
            return False, "\n".join(outputs) if outputs else ""
        
        # 解析命令
        parts = line.split(None, 1)
        if not parts:
            return True, ""
        
        cmd_name = parts[0].lower()
        args_str = parts[1] if len(parts) > 1 else ""
        
        # 查找命令
        cmd = self.commands.get(cmd_name)
        if cmd is None:
            return False, f"'{parts[0]}' 不是内部或外部命令，也不是可运行的程序或批处理文件。"
        
        # 解析参数
        args = cmd.parse_args(args_str)
        
        # 执行
        try:
            return cmd.execute(args)
        except Exception as e:
            logger.error(f"命令执行失败: {cmd_name} {args_str}")
            return False, f"命令执行出错: {e}"


def main():
    """入口函数"""
    print("Made by Crisper")
    shell = CmdShell()
    shell.run()


if __name__ == "__main__":
    main()