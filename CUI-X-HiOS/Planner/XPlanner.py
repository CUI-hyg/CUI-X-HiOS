from mcp.server.fastmcp import FastMCP
import os
import sys
from pathlib import Path
import json
sys.path.append(str(Path(__file__).parent.parent))

mcp = FastMCP()

@mcp.tool()
def TodoCreator(file_path: str,userq: str):
    """创建Todo列表,file_path:文件路径,这是一个字符串,userq:完整的用户问题,这是一个字符串"""
    try:
        process = subprocess.Popen(['sudo','cmd', '/c', f'python Framework\executor.py --agent XSThinking --question 请根据用户问题:{userq}.创建一个合适的ToDoList.只输出内容，不要输出无关内容'], creationflags=subprocess.CREATE_NEW_CONSOLE,)
        process.wait()
        with open('data/result.txt', 'r', encoding='gbk') as f:
            result = f.read()
        return result
    except Exception as e:
        return f"调用智能体 {AgentName} 时出错: {str(e)}"

@mcp.tool()
def WorkFlowCreator(userq: str):
    """创建工作流,userq:完整的用户问题,这是一个字符串"""
    try:
        process = subprocess.Popen(['sudo','cmd', '/c', f'python Framework\executor.py --agent XSThinking --question 请根据用户问题:{userq},创建一个合适的工作流.只输出内容，不要输出无关内容'], creationflags=subprocess.CREATE_NEW_CONSOLE,)
        process.wait()
        with open('data/result.txt', 'r', encoding='gbk') as f:
            result = f.read()
        return result
    except Exception as e:
        return f"运行命令 {command} 时出错: {str(e)}"

if __name__ == "__main__":
    print(f"XPlanner 已成功启动 - studio")
    mcp.run(transport='stdio')
