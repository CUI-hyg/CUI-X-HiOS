import multiprocessing as mp
import sys
import os
import logging
import traceback
from pathlib import Path
import importlib.util
from typing import List, Dict, Any, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentExecutor:
    def __init__(self, max_workers: int = None, debug_mode: bool = False):
        """BaseRunner - Args:  max_workers: 最大工作进程数，默认为CPU核心数  debug_mode: 是否启用调试模式"""
        self.max_workers = max_workers or mp.cpu_count()
        self.debug_mode = debug_mode
        self.project_root = Path(__file__).parent.parent
        self.agents_config = self._load_agents_config()
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)
            logger.info(f"调试模式已启用: {self.max_workers}")
    
    def _load_agents_config(self) -> Dict[str, Any]:
        config_path = self.project_root / "Config.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"无法加载配置文件: {e}，使用默认配置")
            return {"agents": {}}
    
    def _discover_agent_path(self, agent_name: str) -> Optional[Path]:
        agent_dirs = [
            self.project_root / "Agent" / "XWebSearchAgent",
            self.project_root / "Agent" / "XFileOperatorAgent",
            self.project_root / "Agent" / "XBrowserUseAgent",
            self.project_root / "Agent" / "XDIYAgent",
            self.project_root / "Agent" / "XSThinkingAgent",
            self.project_root / "Planner",
            self.project_root / "Framework" / "XGUIUseModele",
        ]
        for agent_dir in agent_dirs:
            if agent_dir.exists():
                agent_file = agent_dir / f"{agent_name}.py"
                if agent_file.exists():
                    return agent_file
        logger.error(f"未找到Agent: {agent_name}")
        return None
    
    def _load_agent_module(self, agent_path: Path):
        """动态加载Agent模块"""
        try:
            project_root_str = str(self.project_root)
            if project_root_str not in sys.path:
                sys.path.insert(0, project_root_str)
            module_name = agent_path.stem
            spec = importlib.util.spec_from_file_location(module_name, agent_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"无法加载模块规范: {agent_path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"加载Agent模块失败 {agent_path}: {e}")
            raise

    def _execute_single_agent(self, agent_task: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个Agent任务"""
        try:
            agent_name = agent_task.get('agent')
            question = agent_task.get('question')
            mode = agent_task.get('mode', 'normal')
            if not agent_name or not question:
                raise ValueError("Agent名称和问题不能为空")
            agent_path = self._discover_agent_path(agent_name)
            if not agent_path:
                return {
                    "status": "error",
                    "agent": agent_name,
                    "question": question,
                    "error": f"Agent {agent_name} 不存在"
                }
            module = self._load_agent_module(agent_path)
            if hasattr(module, 'AgentInit'):
                try:
                    import concurrent.futures
                    import time
                    start_time = time.time()
                    def _execute_agent():
                        return module.AgentInit(question, mode)
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(_execute_agent)
                        result = future.result(timeout=120)
                        
                        execution_time = time.time() - start_time
                        logger.info(f"Agent {agent_name} 执行完成，耗时 {execution_time:.2f} 秒")
                        logger.info(f"执行结果: {result}")
                        logger.info(f"结果类型: {type(result)}")
                        try:
                            save_dir = Path(self.project_root) / "data"
                            save_dir.mkdir(parents=True, exist_ok=True)
                            filename = save_dir / f"result.txt"
                            if result is None:
                                logger.warning("结果为None，保存空字符串")
                                result_str = ""
                            else:
                                result_str = str(result)
                                logger.info(f"结果字符串长度: {len(result_str)}")
                            with open(filename, 'w', encoding='gbk') as f:
                                f.write(result_str)
                            logger.info(f"结果已成功保存至 {filename}")
                        except Exception as e:
                            logger.error(f"保存结果失败: {e}")
                            import traceback
                            logger.error(f"保存结果失败的详细信息: {traceback.format_exc()}")
                        
                        return {
                            "status": "success",
                            "agent": agent_name,
                            "question": question,
                            "result": result,
                            "execution_time": f"{execution_time:.2f}s"
                        }    
                except concurrent.futures.TimeoutError:
                    execution_time = time.time() - start_time
                    logger.error(f"Agent {agent_name} 执行超时，已耗时 {execution_time:.2f} 秒")
                    return {
                        "status": "error",
                        "agent": agent_name,
                        "question": question,
                        "error": f"Agent执行超时(超过120秒)，实际耗时 {execution_time:.2f}s"
                    }
            else:
                return {
                    "status": "error",
                    "agent": agent_name,
                    "question": question,
                    "error": f"Agent {agent_name} 缺少AgentInit接口"
                }  
        except Exception as e:
            logger.error(f"执行Agent任务失败: {e}")
            return {
                "status": "error",
                "agent": agent_task.get('agent'),
                "question": agent_task.get('question'),
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def execute_agents(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量执行Agent任务 - Args: tasks: 任务列表，每个任务格式：
                  {
                      "agent": "Agent名称",
                      "question": "问题内容",
                      "mode": "执行模式"
                  }
        Returns: 执行结果列表
        """
        if not tasks:
            logger.warning("任务列表为空")
            return []
        logger.info(f"开始执行 {len(tasks)} 个Agent任务")
        results = []
        if len(tasks) == 1 or self.max_workers == 1:
            # 单任务或单进程
            for task in tasks:
                result = self._execute_single_agent(task)
                results.append(result)
        else:
            # 多进程并行
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_task = {
                    executor.submit(self._execute_single_agent, task): task
                    for task in tasks
                }
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"进程执行异常: {e}")
                        results.append({
                            "status": "error",
                            "agent": task.get('agent'),
                            "question": task.get('question'),
                            "error": str(e)
                        })
        logger.info(f"完成执行 {len(results)} 个Agent任务")
        return results
    
    def execute_single(self, agent_name: str, question: str, mode: str = "normal") -> Dict[str, Any]:
        """执行单个Agent任务"""
        return self.execute_agents([{
            "agent": agent_name,
            "question": question,
            "mode": mode
        }])[0]

def main():
    """command args"""
    import argparse 
    parser = argparse.ArgumentParser(description='CUIX-HiOS Agent执行器')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--workers', type=int, default=None, help='工作进程数')
    parser.add_argument('--agent', type=str, help='Agent名称')
    parser.add_argument('--question', type=str, help='问题内容')
    parser.add_argument('--mode', type=str, default='normal', help='执行模式')
    parser.add_argument('--batch', type=str, help='批量任务JSON文件路径')
    args = parser.parse_args()
    executor = AgentExecutor(max_workers=args.workers, debug_mode=args.debug)
    if args.batch:
        # 批量任务
        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            results = executor.execute_agents(tasks)
            print(json.dumps(results, ensure_ascii=False, indent=2))
        except Exception as e:
            logger.error(f"批量任务执行失败: {e}")
            sys.exit(1)
    elif args.agent and args.question:
        # 单任务
        result = executor.execute_single(args.agent, args.question, args.mode)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 交互
        if args.debug:
            logger.info("进入交互调试模式...")
            # 示例
            sample_tasks = [
                {"agent": "XWebSearch", "question": "搜索Python教程", "mode": "debug"}
            ]
            results = executor.execute_agents(sample_tasks)
            print("\n执行结果:")
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print("CUIX-HiOS Agent执行器已启动")
            print("使用 --help 查看使用说明")
            print("当前为调试模式，请使用 --debug 参数启用")

if __name__ == "__main__":
    main()