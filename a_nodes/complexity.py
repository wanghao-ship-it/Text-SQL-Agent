from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import interrupt
from State.sql_AgentState import AgentState
from typing import Dict, Any
from a_core.wren_toolkit_wrapper import get_wren_wrapper
from a_core.llm import llm_wren
from a_core.structured_output import ComplexityResult

wrapper = get_wren_wrapper()


def complexity_check_node(state: AgentState) -> Dict[str, Any]:
    sql = state.get("generated_sql")
    # sql = None
    if not sql:
        # logs = state.get("logs", []) + ["complexity_check_node: 没有 SQL 可检查"]
        # return {"is_complex_query": False, "logs": logs}
        raise RuntimeError("sql语句为空，无法判断是否复杂！")

    # 使用结构化输出判断复杂度（你的原有逻辑）
    complex_prompt = """你是一个 SQL 复杂度分析专家。判断 SQL 是否复杂，输出布尔值,
                        复杂"指子查询、多步 CTE 或未定义为 MDL 关系的 JOIN。简单的 GROUP BY 或模型定义的 JOIN 可跳过此步。"""
    user_message = f"请判断这个 SQL 是否复杂：\n{sql}"

    structured_llm = llm_wren.with_structured_output(ComplexityResult, method="function_calling")
    try:
        result = structured_llm.invoke([SystemMessage(content=complex_prompt), HumanMessage(content=user_message)])
        # is_complex = result.is_complex
        is_complex = True
    except Exception as e:
        logs = state.get("logs", []) + [f"complexity_check_node: LLM 判断异常: {str(e)}"]
        return {"is_complex_query": False, "logs": logs}

    logs = state.get("logs", []) + [f"complexity_check_node: 判断复杂度 = {is_complex}"]
    return {"is_complex_query": is_complex, "logs": logs}

if __name__ == '__main__':

    test_state = {
            "question": "你好",
            "messages": [],
            "logs": []
        }
    result = complexity_check_node(test_state)
    print(result)
