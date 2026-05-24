from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from a_core.llm import llm_wren
from State.sql_AgentState import AgentState
from typing import Dict, Any


def final_answer_node(state: AgentState) -> Dict[str, Any]:
    question = state.get("question", "")
    query_data = state.get("query_result")  # 直接就是 data
    if query_data is None:
        raise RuntimeError("sql语句查询结果为空！")
    else:
        content = query_data.get("content", "")

    # if not query_data:
    #     return {"final_answer": "未获取到查询结果"}
    history = state.get("messages", [])  # 获取历史对话

    # 直接喂 content 给 LLM，最省事
    prompt = f"""
    你是一个翻译数据库语句的专家，请你根据用户提问和查询结果生成自然语言答案，不要输出不相关的解释，如果未查询到结果请如实回答：“未查询到结果，数据库没有相关信息！”，不要胡编乱造。
    用户提问：{question}
    查询结果：{content}

    """
    # 结果细节：{query_data}
    response = llm_wren.invoke(history+[HumanMessage(content=prompt)])
    final_answer = response.content.strip()

    return {
        "final_answer": final_answer,
        "messages": [response],
        "logs": state.get("logs", []) + ["final_answer_node: 生成答案成功"]
    }


if __name__ == '__main__':

    test_state = {
        "question": "你好",
        "messages": [],
        "logs": []
    }
    result = final_answer_node(test_state)
    print(result)

