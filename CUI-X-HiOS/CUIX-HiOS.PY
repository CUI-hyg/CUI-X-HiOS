import subprocess
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import os

def AgentInit():
    try:
        # 获取当前脚本所在目录
        configpath = os.path.dirname(os.path.abspath(__file__))
        process = subprocess.Popen(['cmd', '/k', f'python CHOMain.py'], )
        process.wait()
        process.stdout.read().decode('gbk')
        return str(result) if result is not None else "执行完成"
    except Exception as e:
        error_msg = f"Agent执行错误: {str(e)}"
        return error_msg

if __name__ == "__main__":
    print("CUI X-HiOS - 下一代Agent协作系统")
    while True:
        AgentInit()

#creationflags=subprocess.CREATE_NEW_CONSOLE