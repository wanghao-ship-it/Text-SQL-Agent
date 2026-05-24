from langgraph.types import interrupt

from State.sql_AgentState import AgentState
from typing import Dict, Any
from a_core.wren_toolkit_wrapper import get_wren_wrapper

wrapper = get_wren_wrapper()
# 获取工具列表（不含 memory write）
tools = wrapper.get_tools(include_memory_write=False)


def mdl_context_node(state: AgentState) -> Dict:
    """
    获取上下文节点：调用 wren_fetch_context 工具获取数据库的模型、列和关系信息。
    结果存入 state['schema_context']。
    关键节点：任何失败都会强制终止（抛出 GraphInterrupt），避免后续节点基于错误数据运行。
    """
    # 1.从状态中获取用户问题
    question = state.get("question")
    # question = ""
    # todo: 前面已经限制问题不能为空了
    # if not question:
    #     # 如果没有question，返回空列表并记录日志
    #     return {
    #         "schema_context": [],
    #         "logs": state.get("logs", []) + ["mdl_context_node: 问题为空！"]
    #     }
    # 1. 从工具列表中找到对应的工具
    # 2. 从工具列表中找到对应的工具
    fetch_tool = next((t for t in tools if t.name == "wren_fetch_context"), None)
    if not fetch_tool:
        raise RuntimeError("系统错误：未找到 wren_fetch_context 工具。")

    # 2. 调用工具（可能失败）
    try:
        result = fetch_tool.invoke({"question": question})
    except Exception as e:
        raise RuntimeError(f"获取 MDL 上下文时调用工具异常：{str(e)}")

    # 3. 提取工具返回的 MDL 内容（schema_context）
    schema_context = None
    if isinstance(result, dict) and result.get("ok"):
        schema_context = result.get("content")
        if not schema_context:
            data = result.get("data", {})
            schema_context = data.get("schema")

    if not schema_context:
        raise RuntimeError("获取 MDL 上下文失败：工具返回结果为空。")

    # 4. 成功：更新日志并返回
    logs = state.get("logs", []) + [f"fetch_context_node: 成功获取上下文 (长度 {len(schema_context)} 字符)"]
    return {"schema_context": schema_context, "logs": logs}


if __name__ == '__main__':
    test_state = {
        "question": "查询所有员工",
        "messages": [],
        "logs": []
    }
    result = mdl_context_node(test_state)
    print(result)

