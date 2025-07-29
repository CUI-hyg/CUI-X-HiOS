# CUI-X-HiOS 下一代MAS(Multi-Agent System)框架
经过4个月的开发与打磨，CUI X-HiOS AgentFramework 正式亮相啦~

你肯定对这句话不陌生：2025是AIAgent元年。这个框架正是诞生在这个浪潮下的。
- **使命**:集各家之长，创造一个通用、好用、可自定义性强的Agent框架。
- **目标&愿景**:让Ai能够自主创新、自我改进，成为真正的L5级别的AGI.

## What
X-HiOS 就是将记忆、工具、规划、理解、分析等能力接入具有推理与多模态能力的LLM集群中。
打个比方：LLM集群相当于人类的脑子，理解分析是处理问题的能力，规划记忆是解决问题的前提，工具(执行)是完成事情的能力。
也就是说，几乎所有像X-HiOS这样的Agent框架就是连接虚拟空间与现实的通道。

## Why
不管是什么人，在电脑前工作基本是以下流程：
- 搜索大量资料，费时费力。
- 修改各类文件、修BUG，常常花大量的时间。
- 整理数据，提交结果…
- ………

所以，CUI X-HiOS的目标是，通过长期记忆与任务描述，成为你的助手，甚至是你的"替身"，将步骤简化到如下所示：
- 描述需求
- Agent处理任务
- 阅读结果，提交

是不是简单很多？

CUI X-HiOS的使命就是通过精细化需求描述，自动化任务，输出一份完美的报告。

# How
CUI X-HiOS本质是一个AgentOS,通过主Agent调用工具、AGENT来完成任务。
它会先理解，然后调用TaskPlanner，根据ToDo调用具有相应能力的智能体完成任务，并生成报告。

当它执行任务时，你也可以一起工作，结合AgentOS的结论、答案，使你的效率更上一层楼。
甚至，你还可以把你的电脑交给它，它会自动操作你的电脑（正在开发☺️）

##Usage

1.此版本需要添加两个.env文件：一个在主目录下，一个在GUIOperator(必须使用VLLM)
格式如下：
(这里使用OpenAI通用API格式)
```env
OPENAI_API_KEY = sk-你的key
BASE_URL = https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL = Moonshot-Kimi-K2-Instruct
#建议到阿里云百炼获取API,新人有免费额度
#主模型建议使用agent能力强的模型：kimi k2、qwen235b-a22b-*-2507、glm4.5……
#GUIOperator下的建议用qwen-plus
```
另一个
```cmd
//1.临时使用
set API_Key=sk-你的key
//2.永久使用（Windows可在高级系统设置中编辑和查看）
setx API_Key=sk-你的key
```
2. ```cmd git clone https://github.com/CUI-hyg/CUI-X-HiOS.git```

3.创建一个虚拟环境
```python
python -m venv mcp-env
```
4.安装依赖
```python
pip install -r requirements.txt
```
如有缺包，请根据报错解决，建议拉个issue告诉我~
添加.env

运行```CUI-X-HiOS.py```,开始使用吧~

## Feature
1.提升GUIUse稳定性<开发中>
2.构建Workflow体系<规划中>
3.建立memory机制<还未开工>
4.解决Agent库导入问题<找方案中>
5.建立plugin生态<未开工>
6.……

## Tips
1.BUG：Agent导入必须以主目录位置导入，否则会报错（详见代码）->executor.py
2.BUG:要求GUIUse单击一些按钮时会乱点、崩溃（开始菜单就是其一，自己测试一下就知道了）
3.BUG:有时主AI并不会调用XPLANNER，造成任务出现断链
4.欢迎大家修bug,提建议~

## Thanks
- CUI-Hyg:本人,承担主要开发
- Kimi K2:重构了半个架构（😨）
- Qwen3-Coder:修复多个Bug

## 最后
###### 感谢你关注本项目，请点亮一下Star,谢谢~⭐
