import configparser
import os


class Config:
    def __init__(self,config_file="D:/langgraph_wrenai/wren/a_config/config.ini"):
        # 创建配置解析器
        self.config = configparser.ConfigParser()
        # 显式指定 UTF-8 编码读取配置文件
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config.read_file(f)
        self.LLM_KEY = self.config.get("llm","LLM_KEY")
        self.LLM_URL = self.config.get("llm","LLM_URL")
        self.LLM_MODEL = self.config.get("llm","LLM_MODEL")
        self.WREN_DATA_PATH = self.config.get("mysql","WREN_DATA_PATH")
        self.postgres_use = self.config.get("postgres","user")
        self.postgres_password = self.config.get("postgres","password")
        self.postgres_host = self.config.get("postgres","host")
        self.postgres_port = self.config.get("postgres","port")
        self.postgres_database = self.config.get("postgres","database")


config = Config()

if __name__ == '__main__':
    print(config.postgres_database)