import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from executor import AgentExecutor
import json

def demo_single_agent():
    """演示单Agent执行"""
    print("=== 单Agent执行示例 ===")
    
    executor = AgentExecutor(debug_mode=True)
    
    # 执行单个Agent任务
    result = executor.execute_single(
        agent_name="XWebSearch",
        question="搜索一下KimiK2",
        mode="debug"
    )
    
    print("执行结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def demo_batch_agents():
    """演示批量Agent执行"""
    print("\n=== 批量Agent执行示例 ===")
    
    executor = AgentExecutor(max_workers=2, debug_mode=True)
    
    # 定义批量任务
    import json
    with open('batch_tasks.json', 'r', encoding='utf-8') as f:
        tasks = json.load(f)
    # 执行批量任务
    results = executor.execute_agents(tasks)
    
    print("批量执行结果:")
    print(json.dumps(results, ensure_ascii=False, indent=2))

def demo_error_handling():
    """演示错误处理"""
    print("\n=== 错误处理示例 ===")
    
    executor = AgentExecutor(debug_mode=True)
    
    # 测试不存在的Agent
    result = executor.execute_single(
        agent_name="NonExistentAgent",
        question="测试错误处理",
        mode="debug"
    )
    
    print("错误处理结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    print("CUIX-HiOS Agent执行器使用示例")
    print("=" * 50)
    
    try:
        demo_single_agent()
        demo_batch_agents()
        demo_error_handling()
        
    except Exception as e:
        print(f"演示执行失败: {e}")
        import traceback
        traceback.print_exc()