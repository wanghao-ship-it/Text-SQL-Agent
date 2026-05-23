# graph/builder.py
from langgraph.graph import StateGraph, START, END
from a_core.sql_AgentState import AgentState
from a_nodes.read import wren_read_node
from a_nodes.recall import recall_node
from a_nodes.mdl_context import mdl_context_node
from a_nodes.sql_gen import sql_gen_node
from a_nodes.complexity import complexity_check_node
from a_nodes.dry_plan import dry_plan_node
from a_nodes.execute import execute_node
from a_nodes.final_answer import final_answer_node
from a_nodes.base import trim_messages_node
from a_nodes.store_memory import store_memory_node
from a_utils.postgresql_client import create_checkpointer

def build_graph():
    # 1. 初始化图
    builder = StateGraph(AgentState)

    # 2. 添加所有节点
    builder.add_node("read", wren_read_node)
    builder.add_node("recall", recall_node)
    builder.add_node("mdl_context", mdl_context_node)
    builder.add_node("sql_gen", sql_gen_node)
    builder.add_node("complexity_check", complexity_check_node)
    builder.add_node("dry_plan", dry_plan_node)
    builder.add_node("execute", execute_node)
    builder.add_node("final_answer", final_answer_node)
    builder.add_node("trim_messages", trim_messages_node)
    builder.add_node("store_memory", store_memory_node)

    # 3. 定义边（顺序流程）
    builder.add_edge(START, "read")
    builder.add_edge("read", "recall")
    builder.add_edge("recall", "mdl_context")
    builder.add_edge("mdl_context", "sql_gen")

    # 4. 条件分支：从 sql_gen 出发
    builder.add_conditional_edges(
        "sql_gen",
        lambda state: "dry_plan" if state.get("retry_count", 0) > 0 else "complexity_check",
        {
            "dry_plan": "dry_plan",
            "complexity_check": "complexity_check"
        }
    )

    # 5. 条件分支：从 complexity_check 出发
    builder.add_conditional_edges(
        "complexity_check",
        lambda state: "dry_plan" if state.get("is_complex_query") else "execute",
        {
            "dry_plan": "dry_plan",
            "execute": "execute"
        }
    )

    # 6. 后续固定边
    builder.add_edge("dry_plan", "execute")
    builder.add_edge("execute", "final_answer")
    builder.add_edge("final_answer", "trim_messages")
    builder.add_edge("trim_messages", "store_memory")
    builder.add_edge("store_memory", END)

    # 7. 编译图（使用 PostgreSQL 检查点）
    checkpointer = create_checkpointer()
    app = builder.compile(checkpointer=checkpointer)
    return app