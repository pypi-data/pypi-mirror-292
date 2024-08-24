from langchain_openai import OpenAIEmbeddings

from mtmai.mtlibs.aiutils import lcllm_openai_chat


def get_fast_llm():
    llm = lcllm_openai_chat()
    return llm


def get_long_context_llm():
    llm = lcllm_openai_chat()
    return llm


def get_embeding_llm():
    api_key = (
        "10747773f9883cf150558aca1b0dda81af4237916b03d207b8ce645edb40a546"  # together
    )
    base_url = "https://api.together.xyz/v1"
    model = "togethercomputer/m2-bert-80M-32k-retrieval"
    llm_embeding = OpenAIEmbeddings(api_key=api_key, base_url=base_url, model=model)
    return llm_embeding
