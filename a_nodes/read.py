from langchain_core.messages import HumanMessage

from a_core.sql_AgentState import AgentState   # 若你的 AgentState 路径不同，请相应调整


def wren_read_node(state: AgentState) -> dict:
    """
    工作流的第一个节点，读取节点。
    将用户的问题（state["question"]）包装成HumanMessage
    并添加到消息历史 (state['messages']) 中。
    """
    question = state.get("question","").strip()
    # if not question:
    #     question = interrupt("问题不能为空，请输入您的问题：")
    return {
        "messages": [HumanMessage(content=f"用户查询：{question}")]
    }


if __name__ == '__main__':
    test_state = {
        "question": "查询所有员工",
        "messages": [],
        "logs": []
    }
    result = wren_read_node(test_state)
    print(result)
