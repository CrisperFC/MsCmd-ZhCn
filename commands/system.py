"""
系统命令
ver, date, time, ver, systeminfo
"""

from .base import Command
from datetime import datetime


class VerCommand(Command):
    """ver - 显示版本"""
    
    def get_name(self):
        return "ver"
    
    def get_description(self):
        return "显示 Windows 版本。"
    
    def execute(self, args):
        return True, "Microsoft Windows [版本 10.0.19045.3693]\n"


class DateCommand(Command):
    """date - 显示或设置日期"""
    
    def get_name(self):
        return "date"
    
    def get_description(self):
        return "显示或设置日期。"
    
    def execute(self, args):
        now = datetime.now()
        day_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        day_name = day_names[now.weekday()]
        return True, f"当前日期: {now.strftime('%Y-%m-%d')}  {day_name}\n输入新日期: "


class TimeCommand(Command):
    """time - 显示或设置时间"""
    
    def get_name(self):
        return "time"
    
    def get_description(self):
        return "显示或设置系统时间。"
    
    def execute(self, args):
        now = datetime.now()
        return True, f"当前时间: {now.strftime('%H:%M:%S.%f')[:-4]}\n输入新时间: "


class SystemInfoCommand(Command):
    """systeminfo - 显示系统信息"""
    
    def get_name(self):
        return "systeminfo"
    
    def get_description(self):
        return "显示计算机的系统和配置信息。"
    
    def execute(self, args):
        info = r"""
Host Name:                 SIMULATED-PC
OS Name:                   Microsoft Windows 10 Pro
OS Version:                10.0.19045 Build 19045
OS Manufacturer:           Microsoft Corporation
OS Configuration:          Standalone Workstation
OS Build Type:             Multiprocessor Free
System Manufacturer:       SIMULATED
System Model:              SIMULATED-PC
System Type:               x64-based PC
Processor(s):              1 Processor(s) Installed.
                           [01]: Intel64 Family 6 Model 142 Stepping 12
Total Physical Memory:     16,384 MB
Available Physical Memory: 8,192 MB
Virtual Memory: Max Size:  18,432 MB
Virtual Memory: Available: 10,240 MB
Virtual Memory: In Use:    8,192 MB
Page File Location(s):     C:\pagefile.sys
Domain:                    WORKGROUP
Logon Server:              N/A
Hotfix(s):                 N/A
Network Card(s):           1 NIC(s) Installed.
                           [01]: VMware Virtual Ethernet Adapter
                                 Connection Name: Ethernet
                                 DHCP Enabled:    No
                                 IP address(es)
                                 [01]: 192.168.1.100
Hyper-V Requirements:      A hypervisor has been detected. Features required for Hyper-V will not be displayed.
"""
        return True, info


class HelpCommand(Command):
    """help - 显示帮助"""
    
    def get_name(self):
        return "help"
    
    def get_description(self):
        return "提供 Windows 命令的帮助信息。"
    
    def execute(self, args):
        if not hasattr(self.fs, '_commands'):
            return True, "无法获取命令列表。\n"
        
        if args:
            cmd_name = args[0].lower()
            for cmd in self.fs._commands:
                if cmd.get_name().lower() == cmd_name:
                    return True, f"{cmd.get_name().upper()}: {cmd.get_description()}\n"
            return False, f"找不到帮助主题。\n"
        
        # 显示所有命令
        lines = ["THE Following commands are available:"]
        for cmd in self.fs._commands:
            lines.append(f"  {cmd.get_name().upper():12} {cmd.get_description()}")
        lines.append("")
        
        return True, "\n".join(lines)


class ExitCommand(Command):
    """exit - 退出"""
    
    def get_name(self):
        return "exit"
    
    def get_description(self):
        return "退出 CMD 程序。"
    
    def execute(self, args):
        return True, "__EXIT__"


def register_commands(filesystem):
    """注册所有系统命令"""
    return [
        VerCommand(filesystem),
        DateCommand(filesystem),
        TimeCommand(filesystem),
        SystemInfoCommand(filesystem),
        HelpCommand(filesystem),
        ExitCommand(filesystem),
    ]