from langgraph.types import interrupt

from State.sql_AgentState import AgentState
from typing import Dict, Any
from a_core.wren_toolkit_wrapper import get_wren_wrapper

wrapper = get_wren_wrapper()
wrapper.system_prompt()
# 获取工具列表（不含 memory write）
tools = wrapper.get_tools(include_memory_write=False)


def execute_node(state: AgentState) -> Dict[str, Any]:
    """
        SQL执行节点。从状态获取SQL，通过wren_query执行，结果存入query_result。
    """
    sql = state.get("generated_sql")
    # print("sql",sql)
    if not sql:
        logs = state.get("logs", []) + ["execute_node: 没有 SQL 可执行"]
        raise RuntimeError("[execute_node]SQL 为空，无法执行。")

    query_tool = next((t for t in tools if t.name == "wren_query"), None)
    if not query_tool:
        raise RuntimeError("[execute_node]未查询到工具，无法执行。")

    try:
        result = query_tool.invoke({"sql": sql, "limit": 100})
        # print("result",result)
    except Exception as e:
        logs = state.get("logs", []) + [f"execute_node: wren_query 异常: {str(e)}"]
        raise RuntimeError("[execute_node]工具调用失败，无法执行。")

    if isinstance(result, dict) and result.get("ok"):
        data = result.get("data", {})
        query_result = {
            "columns": data.get("columns", []),
            "rows": data.get("rows", []),  # 保持为字典列表，不转换
            "row_count": data.get("row_count", 0),
            "content_truncated": data.get("content_truncated"),  #
            "content": result.get("content")
        }
        logs = state.get("logs", []) + [f"execute_node: SQL 执行成功，返回 {query_result['row_count']} 行"]
        return {"query_result": query_result, "logs": logs}
    else:
        error_msg = result.get("error", {}).get("message", "未知错误")
        logs = state.get("logs", []) + [f"execute_node: SQL 执行失败: {error_msg}"]
        raise RuntimeError(f"[execute_node] 执行结果异常。{error_msg}")


if __name__ == '__main__':

    test_state = {
            "question": "你好",
            "messages": [],
            "logs": []
        }
    result = execute_node(test_state)
    print(result)