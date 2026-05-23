# from langchain_openai import ChatOpenAI
# from base.config import config
# llm_wren = ChatOpenAI(
#     model=config.LLM_MODEL,
#     openai_api_key=config.LLM_KEY,
#     openai_api_base=config.LLM_URL,
#     temperature=0,
#     extra_body={"thinking": {"type": "disabled"}}
# )
# 健壮性处理
from langchain_openai import ChatOpenAI
from a_config.config import config


def create_chat_openai(model=None, api_key=None, api_base=None, temperature=0, extra_body=None):
    try:
        client = ChatOpenAI(
            model=model or config.LLM_MODEL,
            openai_api_key=api_key or config.LLM_KEY,
            openai_api_base=api_base or config.LLM_URL,
            temperature=temperature,
            extra_body=extra_body or {"thinking": {"type": "disabled"}},
            timeout=30
        )
        # 冒烟测试：发送一个极小请求验证连通性和模型有效性
        client.invoke("test")  # 如果模型名错误，这里会直接抛异常
        return client
    except Exception as e:
        print(f"初始化 LLM 出错: {e}")
        raise  # 重新抛出异常，让调用方处理

# 使用
# if __name__ == '__main__':
llm_wren = create_chat_openai()

