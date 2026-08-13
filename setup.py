import sys
import os
import random
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
for i in range(1000):
    print("File found at "+str(hex(random.randint(1, 2**32-1)))+" drives.")

print("Made by Crisper")
time.sleep(1.5)