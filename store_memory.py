from langgraph.types import interrupt

from State.sql_AgentState import AgentState
from typing import Dict, Any
from a_core.wren_toolkit_wrapper import get_wren_wrapper

wrapper = get_wren_wrapper()
wrapper.system_prompt()
# 获取工具列表（不含 memory write）
tools = wrapper.get_tools(include_memory_write=False)


def store_memory_node(state: AgentState) -> Dict[str, Any]:
    """
    存储记忆节点：将成功的 NL→SQL 对存入 Wren 记忆库。
    仅当查询成功且返回有效数据时调用。
    """
    # 1. 获取必要信息
    question = state.get("question")
    sql = state.get("dry_plan_result") or state.get("generated_sql")
    query_result = state.get("query_result")

    if not question or not sql or not query_result:
        raise RuntimeError(f"[store_memory_node]必要信息缺失，无法存储")

    # 2. 从工具列表中找到 wren_store_query 工具
    store_tool = next((t for t in tools if t.name == "wren_store_query"), None)
    if not store_tool:
        logs = state.get("logs", []) + ["store_memory_node: 未找到 wren_store_query 工具,（可能因为 include_memory_write=False），跳过存储"]
        return {"memory_stored": False, "logs": logs}

    # 3. 生成标签（可选）：从查询结果的列名中提取
    columns = query_result.get("columns", [])
    tags = columns if columns else None  # 使用列名作为标签，或者自定义

    # 4. 调用工具存储
    try:
        result = store_tool.invoke({
            "nl": question,
            "sql": sql,
            "tags": tags
        })
    except Exception as e:
        raise RuntimeError(f"[store_memory_node]调用工具失败，无法存储")

    # 5. 解析结果
    if isinstance(result, dict) and result.get("ok"):
        logs = state.get("logs", []) + [f"store_memory_node: 记忆存储成功，标签: {tags}"]
        return {
            "memory_stored": True,
            "logs": logs
        }
    else:
        error_msg = result.get("error", {}).get("message", "未知错误")
        raise RuntimeError(f"[store_memory_node]解析结果失败，错误信息：{error_msg}")
