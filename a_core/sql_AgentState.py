from typing import TypedDict, Literal, Optional, List, Dict, Any, Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

# 1.定义子状态
"""
结构示意：
[
  {"question": "查询上个月总销售额", "sql": "SELECT ..."},
  {"question": "查询产品 A 的销量", "sql": "SELECT ..."}
]
"""


class RecallExample(TypedDict):
    question: str
    sql: str


class QueryData(TypedDict):
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    content_truncated: bool


class QueryResult(TypedDict):
    data: QueryData  # 明确结构
    content: Optional[str]


class ErrorInfo(TypedDict):
    phase: str
    message: str
    dialect_sql: Optional[str]


# 2.定义全局状态(相当与定义字典结构，每次执行的时候都会看这个字典，再进行下一步操作)
class AgentState(TypedDict):

    messages: Annotated[list[AnyMessage], add_messages]
    # ======================
    # 用户输入
    # ======================
    question: str

    # ======================
    # 存放记忆工具召回的问题-sql对
    # ======================
    recalled_queries: Optional[List[RecallExample]]

    # ======================
    # 存放检索的mdl文件内容
    # ======================
    schema_context: Optional[str]

    # ======================
    # 设置模糊问题，判断是否对query有歧义，有的话向用户提问，封装用户返回的答案
    # ======================
    needs_clarification: bool
    clarification_question: Optional[str]
    clarification_answer: Optional[str]

    # ======================
    # 存放生成的sql语句
    # ======================
    generated_sql: Optional[str]

    # ======================
    # 存放是否是复杂问题的结果，验证函数验证的内容，是否需要重新生成的结果
    # ======================
    is_complex_query: bool
    dry_plan_result: Optional[str]
    dry_plan_attempts: int
    validated: bool

    # ======================
    # 存放当前重试的次数，规定最大次数，打印上次失败的错误信息
    # ======================
    retry_count: int
    max_retries: int
    last_error: Optional[ErrorInfo]

    # ======================
    # 存放执行后的返回结果，作用1.提供给final 2.用来判断是否该存入记忆中
    # ======================
    query_result: Optional[QueryResult]

    # ======================
    # 存放答案
    # ======================
    final_answer: Optional[str]

    # ======================
    # 根据query——result里面的行数判断是否存入记忆中
    # ======================
    should_store_memory: bool
    memory_stored: bool

    # ======================
    # Debug / Observability
    # ======================
    logs: List[str]