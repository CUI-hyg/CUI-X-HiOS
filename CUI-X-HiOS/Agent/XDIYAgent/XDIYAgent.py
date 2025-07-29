#这是一个自定义Agent,你可以在里面写自己想要的功能与实现！！Warning:AgentInit函数不要动！！！改了会出错！！！
import sys
sys.path.append("../../FrameWork/")
from MAS import BaseAgent
import os

def AgentInit(userq,use):
    try:
        # 获取当前脚本所在目录
        configpath = os.path.dirname(os.path.abspath(__file__))
        result = BaseAgent.AgentMain(userq, use, configpath)
        return str(result) if result is not None else "执行完成"
    except Exception as e:
        error_msg = f"Agent执行错误: {str(e)}"
        return error_msg

if __name__ == "__main__":
    #userq = input("请输入你的问题:")
    #AgentInit(userq,"yes")
    #若你希望调试这个Agent,解除上面的注释
    print("你未开启调试模式")