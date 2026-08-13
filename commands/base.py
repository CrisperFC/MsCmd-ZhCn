"""
命令基类
所有CMD命令的抽象基类
"""

from abc import ABC, abstractmethod


class Command(ABC):
    """命令基类"""
    
    def __init__(self, filesystem):
        self.fs = filesystem
    
    @abstractmethod
    def get_name(self):
        """返回命令名称"""
        pass
    
    @abstractmethod
    def get_description(self):
        """返回命令描述"""
        pass
    
    @abstractmethod
    def execute(self, args):
        """
        执行命令
        args: 命令参数（已分割为列表）
        返回: (成功布尔值, 输出字符串)
        """
        pass
    
    def parse_args(self, arg_string):
        """解析参数字符串，处理引号"""
        if not arg_string:
            return []
        
        args = []
        current = []
        in_quotes = False
        
        for char in arg_string:
            if char == '"':
                in_quotes = not in_quotes
            elif char in (' ', '\t') and not in_quotes:
                if current:
                    args.append(''.join(current))
                    current = []
            else:
                current.append(char)
        
        if current:
            args.append(''.join(current))
        
        return args