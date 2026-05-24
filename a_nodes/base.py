from typing import Dict, Any
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from a_core.sql_AgentState import AgentState   # 若你的 AgentState 路径不同，请相应调整


def trim_messages_node(state: AgentState) -> Dict[str, Any]:
    """
    独立的修剪节点：对消息历史进行修剪，防止超出 LLM 上下文窗口。
    该节点会更新 state['messages']，后续节点将使用修剪后的历史。
    """
    raw_messages = state.get("messages", [])

    # 如果历史为空，无需修剪
    if not raw_messages:
        return {"logs": state.get("logs", []) + ["trim_messages_node: 消息历史为空，跳过修剪"]}

    token_count = count_tokens_approximately(raw_messages)
    max_tokens = 10000  # 你的限制

    if token_count <= max_tokens:
        return {
            "messages": raw_messages,
            "logs": state.get("logs", []) + ["trim_messages_node: Token 未超限，跳过修剪"]
        }

    # 执行修剪
    trimmed_messages = trim_messages(
        raw_messages,
        strategy="last",  # 保留最新的消息
        token_counter=count_tokens_approximately,
        max_tokens=1000,  # 根据模型窗口调整
        start_on="human",  # 保证以 HumanMessage 开头
        end_on=("human", "tool"),  # 保证以 HumanMessage 或 ToolMessage 结尾
    )

    logs = state.get("logs", []) + [
        f"trim_messages_node: 修剪消息，从 {len(raw_messages)} 条减少到 {len(trimmed_messages)} 条"]
    return {
        "messages": trimmed_messages,
        "logs": logs
    }
