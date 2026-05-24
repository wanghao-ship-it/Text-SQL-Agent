from langgraph.types import interrupt

from State.sql_AgentState import AgentState
from typing import Dict, Any
from a_core.wren_toolkit_wrapper import get_wren_wrapper

wrapper = get_wren_wrapper()
wrapper.system_prompt()
# 获取工具列表（不含 memory write）
tools = wrapper.get_tools(include_memory_write=False)


def dry_plan_node(state: AgentState) -> Dict[str, Any]:
    sql = state.get("generated_sql")
    attempt = state.get("dry_plan_attempts", 0)
    # todo： 测试重试机制，改动SQL语句
    # sql = sql.replace("WITH", "FROM nonexistent_table, ")  # 一定失败
    if not sql:
        raise RuntimeError("SQL 为空，无法验证。")

    dry_tool = next((t for t in tools if t.name == "wren_dry_plan"), None)
    if not dry_tool:
        raise RuntimeError("未找到验证工具函数，无法验证。")

    result = dry_tool.invoke({"sql": sql})
    if isinstance(result, dict) and result.get("ok"):
        dialect_sql = result.get("data", {}).get("dialect_sql", "")
        return {"dry_plan_result": dialect_sql, "validated": True,
                "logs": state.get("logs", []) + ["dry_plan_node: 验证成功"]}
    else:
        error_msg = result.get("error", {}).get("message", "未知错误")

        if attempt >= 1:
            raise RuntimeError("无法修复：人工修复后仍验证失败，流程终止。")
        # 第一次失败，中断并等待人工修复（不修改 attempt，由外部处理）
        updated = interrupt(
            {
                "instruction": f"SQL 验证失败：{error_msg}请修正 SQL。",
                "content": state["generated_sql"],
            })
        # interrupt(f"SQL 验证失败：{error_msg}请修正 SQL。", "content": state[],)
        return {"generated_sql" :updated}

    # except Exception as e:
    #
    #     raise RuntimeError(f"工具调用异常：{str(e)}")

if __name__ == '__main__':

    test_state = {
            "question": "你好",
            "messages": [],
            "logs": []
        }
    result = dry_plan_node(test_state)
    print(result)
