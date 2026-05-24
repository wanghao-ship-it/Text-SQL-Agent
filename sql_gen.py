from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from a_core.llm import llm_wren
from a_core.structured_output import SQLResponse
from State.sql_AgentState import AgentState
from typing import Dict, Any
from a_core.wren_toolkit_wrapper import get_wren_wrapper

wrapper = get_wren_wrapper()
# wrapper.system_prompt()

def sql_gen_node(state: AgentState) -> Dict[str, Any]:
    # 1.获取状态里面的关键信息
    question = state.get("question", "")
    recalled = state.get("recalled_queries", [])
    schema = state.get("schema_context", "")

    # 2.构建系统提示词
    system_prompt = wrapper.system_prompt()

    # 3.构建few-shot示例文本
    few_shot_text = "\n\n".join([
        f"【历史问题】{ex['question']}\n【对应 SQL】{ex['sql']}"
        for ex in recalled
    ])
    # ========== 新增：构建错误修正提示（仅重试时） ==========
    # last_error = state.get("last_error")
    # error_hint = ""
    # if last_error:
    #     error_hint = f"""
    # 【⚠️ 上次生成的 SQL 验证失败，请根据错误信息修正】
    # 错误阶段：{last_error.get('phase', '未知')}
    # 错误信息：{last_error.get('message', '未知')}
    # 请仔细分析错误原因，修改 SQL 语句，不要重复之前的错误。
    # """
    example = """
    示例1： "question": "公司成立多少年了",
           "SELECT '公司成立多少年这个问题无法从现有数据库表中获取，因为数据库中没有存储公司成立日期的信息。' AS answer;"
    示例2："question": "你能干什么",
          "SELECT '我可以帮你查询公司员工、部门信息，例如：各部门薪资情况、员工分布、高薪员工统计等。请问你想了解什么？' AS answer;"
    """

    # 4. 构建用户消息
    user_message = f"""
    【数据库上下文】
    {schema}

    【历史示例】
    {few_shot_text}
    【当前问题】
    {question}
    **注意事项**：请先严格根据数据库上下文判断能不能生成用户提问对应的SQL语句，如果不能，请学习例子生成sql语句，不要照抄回答内容！
    【例子】
    {example}

    请**只生成一条 SQL 语句**，即使问题包含多个部分，也要通过子查询或 CTE 合并成一条语句。
    不要使用分号分隔多条语句。只输出 SQL语句，不要文字，多余解释，多余符号（比如```）。

    **重要限制**：如果使用了 'IN' 或 'NOT IN'，且子查询中包含 'LIMIT'，你必须将 'LIMIT' 子查询包裹在一个派生表中，正确示例如下：
    SELECT e.job, AVG(e.sal) AS avg_salary
    FROM emp AS e
    LEFT JOIN dept AS d ON e.deptno = d.deptno
    WHERE d.dname IN ('FINANCE', 'IT')
      AND e.job NOT IN (
        SELECT job FROM (
            SELECT job
            FROM emp AS e2
            LEFT JOIN dept AS d2 ON e2.deptno = d2.deptno
            WHERE d2.dname IN ('FINANCE', 'IT')
            GROUP BY e2.job
            ORDER BY COUNT(*) DESC
            LIMIT 3
        ) AS top_3_jobs
      )
    GROUP BY e.job;
    不要写成WHERE column NOT IN (SELECT ... LIMIT 3)，否则会报错。
    """
    # 5. 调用 LLM,加上历史记忆
    messages = state.get("messages", []) + [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    structured_llm = llm_wren.with_structured_output(
        SQLResponse,
        method="function_calling"
    )

    response = structured_llm.invoke(messages)
    # print("response",response)
    generated_sql = response.sql.strip()  # 直接取 sql 字段
    # print("generated_sql===",generated_sql)

    # 6. 记录日志并返回
    logs = state.get("logs", []) + [f"sql_gen_node: 生成 SQL 成功"]
    new_messages = [
        # SystemMessage(content=system_prompt),  # 系统提示词
        # HumanMessage(content=user_message),  # 用户问题
        AIMessage(content=generated_sql)
    ]

    return {"generated_sql": generated_sql,
            "logs": logs,
            "messages": new_messages,
            }

if __name__ == '__main__':

    test_state = {
        "question": "你好",
        "messages": [],
        "logs": []
    }
    result = sql_gen_node(test_state)
    print(result)
