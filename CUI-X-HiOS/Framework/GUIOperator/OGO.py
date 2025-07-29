from mcp.server.fastmcp import FastMCP
import os
import pyautogui as pag

mcp = FastMCP()

@mcp.tool()
def openfile(file_path: str):
    """打开指定位置的文件,file_path:文件路径,这是一个字符串"""
    try:
        pag.alert(text='你确定要运行命令吗？', title='CUISafe - 安全提示', button='OK')

        os.startfile(file_path)
        return f"文件 {file_path} 已成功打开。"
    except Exception as e:
        return f"打开文件 {file_path} 时出错: {str(e)}"

@mcp.tool()
def ImagePosition(userq: str):
    """这是一个图片定位工具,userq:用户输入,这是一个字符串"""
    from dashscope import MultiModalConversation
    try:
        local_path = "D:\My_Code\_MyCode_py\AI\CUI-X-HiOS\Framework\GUIOperator\screenshot.png"
        image_path = f"file://{local_path}"
        messages = [{"role": "system",
                "content": [{"text": "你是CUI X-ImagePostition Agent,专门用于图片定位。请根据用户内容,定位screenshot.png中用户所要求定位的图片元素(如用户输入‘开始菜单’,那么你要找到开始菜单的图标位置,返回X轴Y轴),并返回元素的位置,格式为:X,Y。以下信息必须使用:系统的分辨率为2560 x 1600,系统版本为Win11,你需要准确定位元素位置"}]},


                {'role':'user',
                'content': [{'image': image_path},
                            {'text': userq}]}]
        response = MultiModalConversation.call(
            api_key=os.getenv('Api_Key'),
            model='qwen-vl-plus-latest',
            messages=messages)
        return response["output"]["choices"][0]["message"]["content"][0]["text"]
    except Exception as e:
        return f"定位图片 {userq} 时出错: {str(e)}"

@mcp.tool()
def click(x: str, y: str, button: str = 'left', clicks: int = 1):
    """点击指定位置,x:这是一个数字,为横轴,y:这是一个数字,为纵轴,button:鼠标按键('left', 'right', 'middle'),clicks:点击次数"""
    try:
        xz = int(x)
        yz = int(y)
        pag.alert(text='你确定要点击该位置吗？', title='CUISafe - 安全提示', button='OK')
        pag.click(x=xz, y=yz, clicks=clicks, interval=0.25, button=button)
        return f"已点击位置 ({x}, {y}), 按键: {button}, 次数: {clicks}"
    except Exception as e:
        return f"点击位置 ({x}, {y}) 时出错: {str(e)}"

@mcp.tool()
def right_click(x: str, y: str):
    """右键点击指定位置,x:这是一个数字,为横轴,y:这是一个数字,为纵轴"""
    try:
        xz = int(x)
        yz = int(y)
        pag.alert(text='你确定要右键点击该位置吗？', title='CUISafe - 安全提示', button='OK')
        pag.click(x=xz, y=yz, button='right')
        return f"已右键点击位置 ({x}, {y})"
    except Exception as e:
        return f"右键点击位置 ({x}, {y}) 时出错: {str(e)}"

@mcp.tool()
def input_text(x: str, y: str, text: str):
    """在指定位置输入文本,x:这是一个数字,为横轴,y:这是一个数字,为纵轴,text:这是要输入的文本"""
    try:
        xz = int(x)
        yz = int(y)
        pag.click(x=xz, y=yz)  # 先点击位置确保焦点
        pag.write(text, interval=0.2)
        return f"已输入文本 ({x}, {y}): {text}"
    except Exception as e:
        return f"在位置 ({x}, {y}) 输入文本时出错: {str(e)}"

@mcp.tool()
def press_key(key: str):
    """按下指定按键,key:按键名称"""
    try:
        pag.press(key)
        return f"已按下按键: {key}"
    except Exception as e:
        return f"按下按键 {key} 时出错: {str(e)}"

@mcp.tool()
def press_keys(keys: list):
    """按下多个按键,keys:按键名称列表"""
    try:
        for key in keys:
            pag.press(key)
        return f"已按下按键序列: {', '.join(keys)}"
    except Exception as e:
        return f"按下按键序列 {keys} 时出错: {str(e)}"

@mcp.tool()
def screenshot():
    """这是一个截图工具"""
    try:
        pag.screenshot('screenshot.png')
        return f"已截图"
    except Exception as e:
        return f"截图时出错: {str(e)}"

if __name__ == "__main__":
    print(f"OS&GUI Operator 已成功启动 - studio")
    mcp.run(transport='stdio')
