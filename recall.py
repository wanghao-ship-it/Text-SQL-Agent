from State.sql_AgentState import AgentState
from typing import Dict, Any
from a_core.wren_toolkit_wrapper import get_wren_wrapper

wrapper = get_wren_wrapper()
wrapper.system_prompt()
# 获取工具列表（不含 memory write）
tools = wrapper.get_tools(include_memory_write=False)

def recall_node(state: AgentState) -> Dict[str,Any]:
    """
    记忆召回节点。
     从 Wren 记忆库 (query_history.lance) 中检索与用户问题相似的历史 NL→SQL 对。
    结果将存入 state['recalled_queries']，作为后续生成 SQL 的少样本示例。
    """
    # 1.从状态中获取用户问题
    question = state.get("question")
    if not question:
        # 如果没有question，返回空列表并记录日志
        return {
            "recalled_queries":[],
            "logs":state.get("logs", []) + ["recall_node: 未提供问题，跳过召回"]
        }
    # 1. 从工具列表中找到对应的工具
    recall_tool = next(t for t in tools if t.name == "wren_recall_queries")

    # 2. 直接调用工具（不需要 LLM）
    try:
        result = recall_tool.invoke({
            "question": question,
            "limit": 3,  # 可配置

        })
    except Exception as e:
        # 处理异常
        logs = state.get("logs", []) + [f"recall_node 错误: {str(e)}"]
        return {"recalled_queries": [], "logs": logs}
    # 提取wren——recall函数的返回值
    recalled = []
    if isinstance(result, dict) and result.get("ok"):
        # 从 data.results 提取
        data = result.get("data", {})
        results = data.get("results", [])
        if isinstance(results, list):
            for item in results:
                # 有些 item 可能没有 nl_query 或 sql_query，需要健壮处理
                nl = item.get("nl_query") or item.get("text")  # 兼容不同字段名
                sql = item.get("sql_query")
                if nl and sql:
                    recalled.append({"question": nl, "sql": sql})
            # 如果 results 为空，recalled 就是空列表
        else:
            # 如果 results 不是列表，记录异常
            logs = state.get("logs", []) + [f"recall_node: data.results 不是列表"]
            return {"recalled_queries": [], "logs": logs}
    else:
        # 如果 result 不是 dict 或者 ok 为 False
        logs = state.get("logs", []) + [f"recall_node: 工具返回异常: {result}"]
        return {"recalled_queries": [], "logs": logs}

    logs = state.get("logs", []) + [f"recall_node: 召回 {len(recalled)} 条记忆"]
    return {"recalled_queries": recalled, "logs": logs}


if __name__ == '__main__':
    test_state = {
        "question": "查询所有员工",
        "messages": [],
        "logs": []
    }
    result = recall_node(test_state)
    print(result)
