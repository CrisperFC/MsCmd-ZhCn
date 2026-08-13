"""简单测试脚本"""
from shells.cmd_shell import CmdShell

shell = CmdShell()
print("命令数量:", len(shell.commands))
print()

print("测试dir:")
ok, out = shell.execute_command('dir')
print(out[:200] if out else "空输出")
print()

print("测试ver:")
ok, out = shell.execute_command('ver')
print(out)

print("测试date:")
ok, out = shell.execute_command('date')
print(out)

print("测试help:")
ok, out = shell.execute_command('help')
print(out[:300])

print("\n所有测试完成!")