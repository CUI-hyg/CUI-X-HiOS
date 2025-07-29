import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import json
import os
import re
from lxml import etree
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from dotenv import load_dotenv

class MCPClient:
    def __init__(self,path):

        # 初始化会话和客户端
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        # 加载.env 文件
        self.load_env()

        # Agent Config 定义加载
        self.path = path

        # 从环境变量中获取LLM配置
        self.load_llmcfg()

        # 存储对话历史
        self.messages = []

        # 加载系统提示模板
        self.system_prompt = self.load_prompt()

        # 加载MCP服务器配置
        self.mcp_servers = self.load_cfg()

    def load_env(self):
        """加载.env 文件"""
        load_dotenv()

    def load_llmcfg(self):
        """获取LLM配置"""
        self.API_KEY = os.getenv("API_KEY")
        self.BASE_URL = os.getenv("BASE_URL")   
        self.MODEL = os.getenv("MODEL")
        self.client = OpenAI(api_key=self.API_KEY, base_url=self.BASE_URL)

    def load_prompt(self):
        """加载系统提示"""
        prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.path+"/agent_prompt.txt" if self.path else "Agent_Prompt.txt")
        try:
            with open(prompt_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise RuntimeError("Agent_Prompt.txt 文件未找到，请确保文件存在。")

    def load_cfg(self):
        """加载MCP配置"""
        mcp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.path+"/mcp.json" if self.path else "mcp.json")
        try:
            with open(mcp_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get('mcpServers', {})
        except FileNotFoundError:
            raise RuntimeError("mcp.json 文件未找到，请确保配置文件存在。")
        except json.JSONDecodeError:
            raise RuntimeError("mcp.json 文件格式错误，请检查JSON内容。")
        except Exception as e:
            raise RuntimeError(f"读取 mcp.json 时发生错误: {e}")


    async def server_cnt(self, server_name: str):
        """连接MCP"""
        server_config = self.mcp_servers.get(server_name)

        if not server_config:
            raise ValueError(f"未找到 '{server_name}' 的MCP配置。请检查配置。")

        # 提取配置参数
        command, args, env = self.extr_toolconfig(server_config)

        # 合并环境变量（可选，保留系统环境变量）
        merged_env = self.env_process(env)
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=merged_env,
        )

        # 启动stdio客户端并建立会话
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        # 初始化MCP会话
        await self.session.initialize()

        # 获取可用工具并更新系统提示
        response = await self.session.list_tools()
        available_tools = self.fmt_tool(server_name, response.tools)
        self.system_prompt = self.system_prompt.replace("<$MCP_INFO$>", "\n".join(available_tools))
        print(f"成功连接到 {server_name} 服务，可用工具：{[tool.name for tool in response.tools]}")

    def extr_toolconfig(self, server_config):
        """提取MCP配置"""
        command = server_config.get("command")
        args = server_config.get("args", [])
        env = server_config.get("env", {})

        if not command or not isinstance(args, list):
            raise ValueError("MCP服务器配置缺少必要的 'command' 或 'args'。")

        return command, args, env

    def env_process(self, env):
        """合并环境变量，保留系统环境变量"""
        merged_env = os.environ.copy()
        merged_env.update(env)
        return merged_env

    def fmt_tool(self, server_name, tools):
        """格式化工具信息"""
        return [
            f'##{server_name}\n### Available Tools\n- {tool.name}\n{tool.description}\n{json.dumps(tool.inputSchema)}'
            for tool in tools
        ]

    async def base_use(self, query: str) -> str:
        """处理用户问题"""
        self.messages = []
        # 初始化时添加系统提示
        self.messages.append({"role": "system", "content": self.system_prompt})
        self.messages.append({"role": "user", "content": query})


        while True:
            # 调用LLM（启用流模式）
            response = await self.llm_call()

            # pag.screenshot('screenshot.png')

            if 'Mcp调用终止' in response.lower():
                return response

            # 判断是否需要调用MCP工具
            if '<use_mcp_tool>' not in response:
                return response

            try:
                server_name, tool_name, tool_args = self.tool_str_par(response)
            except Exception as e:
                return f"解析工具调用失败: {e}"

            # 调用MCP工具
            tool_result = await self.mcp_use(tool_name, tool_args)

            # 将工具调用和结果反馈给LLM
            self.messages.append({"role": "assistant", "content": response})
            self.messages.append({
                "role": "user",
                "content": f"[工具 {tool_name} 返回: {tool_result}]"
            })

        # 第二次调用LLM（启用流模式）
        second_response = await self.llm_call()
        return second_response

    async def llm_call(self):
        """调用LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                max_tokens=1024,
                messages=self.messages,
                stream=True
            )
        except Exception as e:
            raise RuntimeError(f"LLM调用失败: {str(e)}")

        content_chunks = []
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content_chunks.append(chunk.choices[0].delta.content)
        return ''.join(content_chunks)

    async def mcp_use(self, tool_name, tool_args):
        """调用MCP"""
        try:
            result = await self.session.call_tool(tool_name, tool_args)
            print(f"[调用工具 {tool_name} 参数: {tool_args}]")
            print("-" * 80)
            if result and result.content and len(result.content) > 0 and hasattr(result.content[0], 'text'):
                tool_result = result.content[0].text
            else:
                tool_result = str(result) if result else "无返回内容"
            print("结果:", tool_result)
            return tool_result
        except Exception as e:
            raise RuntimeError(f"调用MCP {tool_name} 失败: {str(e)}")

    def tool_str_par(self, tool_string: str) -> tuple[str, str, dict]:
        """解析LLMToolCall字符串"""
        match = re.search(r"<use_mcp_tool>(.*?)</use_mcp_tool>", tool_string, re.DOTALL)
        if not match:
            raise ValueError("ToolCall调用Code未找到")

        tool_xml = match.group(1).strip()
        try:
            root = etree.fromstring(f"<root>{tool_xml}</root>")
        except etree.XMLSyntaxError as e:
            raise ValueError(f"ToolCall - XML解析失败: {e}")

        server_name = root.findtext("server_name", default="github")
        if server_name not in self.mcp_servers:
            raise ValueError(f"ToolCall调用的 '{server_name}' 没有配置。")

        tool_name = root.findtext("tool_name")
        arguments = root.findtext("arguments")

        if not tool_name or not arguments:
            raise ValueError("缺少参数")

        try:
            tool_args = json.loads(arguments)
        except json.JSONDecodeError:
            raise ValueError("工具解析失败")

        return server_name, tool_name, tool_args

    async def aichat(self,mode,userq):
        """聊天调用入口"""
        self.messages = []
        if mode == "yes":
            response = await self.base_use(userq)
            return response
        else:
            try:
                response = await self.base_use(userq)
                return response
            except Exception as e:
                return f"执行错误: {str(e)}"

    async def cleanup(self):
        await self.exit_stack.aclose()

async def cnt_server(client):
    """连接 mcp"""
    servers = list(client.mcp_servers.keys())
    if not servers:
        print("错误：未在配置中找到任何MCP。")
        return None
    # 选择第一个服务器
    first_server: str = servers[0]
    return first_server

async def Run(agentcall,userq,path):
    client: MCPClient = MCPClient(path)
    try:
        selected_server: str = await cnt_server(client)
        if selected_server is None:
            return "未选择任何MCP服务器，程序退出。"
        # 添加连接超时处理
        try:
            await asyncio.wait_for(client.server_cnt(selected_server), timeout=40.0)
        except asyncio.TimeoutError:
            return f"连接服务器 {selected_server} 超时（40秒）"

        if agentcall == "yes":
            result = await client.aichat("yes",userq)
            return result
        else:
            result = await client.aichat("no",userq)
            return result
    except ConnectionRefusedError:
        return f"连接失败，请检查 {selected_server} 是否有问题"
    except Exception as e:
        return f"ERR: {str(e)}"
    finally:
        await client.cleanup()

def AgentMain(userq,use,path):
    try:
        import asyncio
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(Run(use,userq,path))
            return str(result) if result is not None else "执行完成"
        finally:
            try:
                loop.close()
            except:
                pass
    except Exception as e:
        error_msg = f"Agent执行错误: {str(e)}"
        print(error_msg)

if __name__ == "__main__":
    print("你没有启用调试模式")
    #asyncio.run(main("no","","")) # 调试模式