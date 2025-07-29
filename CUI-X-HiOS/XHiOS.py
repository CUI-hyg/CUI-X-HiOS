from mcp.server.fastmcp import FastMCP
import os
import pyautogui as pag
import sys
import subprocess
from pathlib import Path
import json
sys.path.append(str(Path(__file__).parent.parent))

mcp = FastMCP()

@mcp.tool()
def openfile(file_path: str):
    """打开指定位置的文件,file_path:文件路径,这是一个字符串"""
    try:
        pag.alert(text='你确定要打开文件吗？', title='CUISafe - 安全提示', button='OK')
        os.startfile(file_path)
        return f"文件 {file_path} 已成功打开。"
    except Exception as e:
        return f"打开文件 {file_path} 时出错: {str(e)}"

@mcp.tool()
def RunCommand(command: str):
    """运行指定的命令,command:cmd可用命令,这是一个字符串。请注意:当前系统为Windows系统,请确保命令格式正确"""
    try:
        pag.alert(text='你确定要运行命令吗？这可能会造成严重后果。命令：' + command, title='CUISafe - 安全提示', button='OK')
        os.system(command)
        return f"命令 {command} 已成功运行。"
    except Exception as e:
        return f"运行命令 {command} 时出错: {str(e)}"

@mcp.tool()
def AgentCalling(AgentName: str, UserQuestion: str):
    """
    调用指定的智能体：
    AgentName:智能体名称,
    UserQuestion:用户输入的完整问题,这是一个字符串。当前可用Agent有:
    XWebSearch:用来搜索,
    XFileOperator:用来操作文件,
    XBrowserUse:用来使用浏览器,
    XDIYAgent:用来自定义操作,
    XGUIUse:用来操作GUI,一般情况下,当需要打开、输入类的操作时,调用本智能体。
    XThinkingAgent:用来思考,
    根据用户问题调用不同的智能体。
    你只可以填列出的智能体名称
    """
    try:
        process = subprocess.Popen(['sudo','cmd', '/c', f'python Framework\executor.py --agent {AgentName} --question {UserQuestion}'], creationflags=subprocess.CREATE_NEW_CONSOLE,)
        process.wait()
        with open('data/result.txt', 'r', encoding='gbk') as f:
            result = f.read()
        return result
    except Exception as e:
        return f"调用智能体 {AgentName} 时出错: {str(e)}"

@mcp.tool()
def TodoCreator(userq:str):
    """创建Todo列表,userq:完整的用户问题,这是一个字符串。如果任务很简单，如打开浏览器等，无需调用本MCP,直接完成任务即可。如果任务比较复杂，则这个MCP的优先级高于一切,在执行复杂任务之前，必须先调用它,了解任务"""
    try:
        process = subprocess.Popen(['sudo','cmd', '/c', f'python Framework\executor.py --agent CUIXPlanner --question 请根据用户问题:{userq},创建一个合适的ToDoList.只输出内容，不要输出无关内容'], creationflags=subprocess.CREATE_NEW_CONSOLE,)
        process.wait()
        with open('data/result.txt', 'r', encoding='gbk') as f:
            result = f.read()
        with open('data/TodoList.txt', 'w', encoding='gbk') as f:
            f.write(result)
        return result
    except Exception as e:
        return f"调用 X-Planner 时出错: {str(e)}"

if __name__ == "__main__":
    print(f"XHiOSMainServer 已成功启动 - studio模式")
    mcp.run(transport='stdio')
