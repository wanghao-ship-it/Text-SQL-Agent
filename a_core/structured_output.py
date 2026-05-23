from pydantic import BaseModel, Field


class ComplexityResult(BaseModel):
    """SQL 复杂度判断结果"""
    is_complex: bool = Field(
        description="SQL 是否复杂。复杂为 true，简单为 false。"
    )
    # 可选：加上理由字段，方便调试
    # reason: str = Field(None, description="判断依据（可选）")


class SQLResponse(BaseModel):
    sql: str = Field(
        description="""
        仅一条纯净的 SQL 语句,不要使用分号分隔多条语句,不要文字，多余解释，多余符号（比如```）。
        """
    )