from psycopg import Connection
from langgraph.checkpoint.postgres import PostgresSaver
from base.config import config

DB_URI = f"postgresql://{config.postgres_use}:{config.postgres_password}@{config.postgres_host}:{config.postgres_port}/{config.postgres_database}"


def create_checkpointer(db_uri=DB_URI):
    try:
        conn = Connection.connect(db_uri)
        checkpointer = PostgresSaver(conn)
        checkpointer.setup()
        # print("✅ 成功连接 PostgreSQL 数据库")
        return checkpointer
    except Exception as e:
        print(f"❌ 连接 PostgreSQL 数据库失败: {e}")
        raise RuntimeError("数据库连接错误，请检查 PostgreSQL 服务是否已启动") from e


if __name__ == '__main__':

    create_checkpointer()