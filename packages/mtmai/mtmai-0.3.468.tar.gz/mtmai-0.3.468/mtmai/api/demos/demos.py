import asyncio
import json
import logging
import threading

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger()


# @router.get("/demos/yaml")
# async def demo_yaml():
#     with Path.open("configs/mtsite_demo.yml") as file:
#         return yaml.safe_load(file)


# @router.get("/langchain/hello")
# async def langchain_hello():
#     """简单使用 langchain 语言模型."""
#     llm = lcllm_openai_chat("groq/llama3-8b-8192")
#     return llm.invoke("how can langsmith help with testing?")


# @router.get("/langchain/hello2")
# async def langchain_hello2():
#     """简单使用 langchain 语言模型."""
#     messages = [
#         SystemMessage(content="You're a helpful assistant"),
#         HumanMessage(content="What is the purpose of model regularization?"),
#     ]
#     llm = lcllm_openai_chat("groq/llama3-8b-8192")
#     return llm.invoke(messages)


# @router.get("/langchain/hello3")
# async def langchain_hello3():
#     """简单使用 langchain 语言模型(stream)."""
#     messages = [
#         SystemMessage(content="You're a helpful assistant"),
#         HumanMessage(content="What is the purpose of model regularization?"),
#     ]
#     llm = lcllm_openai_chat("groq/llama3-8b-8192")
#     for chunk in llm.stream(messages):
#         print(chunk.content, end="", flush=True)


# @router.get("/langchain/hello4")
# async def langchain_hello4():
#     """简单使用 langchain 语言模型(batch)."""
#     messages = [
#         SystemMessage(content="You're a helpful assistant"),
#         HumanMessage(content="What is the purpose of model regularization?"),
#     ]
#     llm = lcllm_openai_chat("groq/llama3-8b-8192")
#     return llm.batch([messages])


# @router.get("/langchain/hello5")
# async def langchain_hello5():
#     """简单使用 langchain 语言模型(async)."""
#     messages = [
#         SystemMessage(content="You're a helpful assistant"),
#         HumanMessage(content="What is the purpose of model regularization?"),
#     ]
#     llm = lcllm_openai_chat("groq/llama3-8b-8192")
#     # 异步调用
#     return llm.ainvoke(messages)

#     # 或者: 异步流
#     # async for chunk in llm.astream(messages):
#     # print(chunk.content, end="", flush=True)


# @tool
# def add(a: int, b: int) -> int:
#     """Adds a and b.

#     Args:
#         a: first int
#         b: second int
#     """
#     return a + b


# @tool
# def multiply(a: int, b: int) -> int:
#     """Multiplies a and b.

#     Args:
#         a: first int
#         b: second int
#     """
#     return a * b


# tools = [add, multiply]


# # Note that the docstrings here are crucial, as they will be passed along
# # to the model along with the class name.
# class Add(BaseModel):
#     """Add two integers together."""

#     a: int = Field(..., description="First integer")
#     b: int = Field(..., description="Second integer")


# class Multiply(BaseModel):
#     """Multiply two integers together."""

#     a: int = Field(..., description="First integer")
#     b: int = Field(..., description="Second integer")


# tools2 = [add, multiply]


# @router.get("/langchain/tool")
# async def langchain_tool():
#     """Langchain tool use."""
#     messages = [
#         SystemMessage(content="You're a helpful assistant"),
#         HumanMessage(content="What is the purpose of model regularization?"),
#     ]
#     llm = lcllm_openai_chat("groq/llama3-8b-8192")
#     llm.bind_tools(tools)
#     return await llm.invoke(messages)

#     # 或者: 异步流
#     # async for chunk in llm.astream(messages):
#     # print(chunk.content, end="", flush=True)


# @router.get("/user")
# async def langchain_tool():
#     """Langchain tool use."""
#     messages = [
#         SystemMessage(content="You're a helpful assistant"),
#         HumanMessage(content="What is the purpose of model regularization?"),
#     ]
#     llm = lcllm_openai_chat("groq/llama3-8b-8192")
#     llm.bind_tools(tools)
#     return await llm.invoke(messages)


counter = 0
stop_event = asyncio.Event()
counter_lock = threading.Lock()


async def increment_counter(limit: int):
    global counter
    print("increment_counter call")
    while counter <= limit:
        if stop_event.is_set():
            print("Counter stopped by user.")
            break
        await asyncio.sleep(1)
        with counter_lock:
            counter += 1
        print(f"Counter incremented to {counter}")


def start_increment_counter(limit):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(increment_counter(limit))


@router.get("/counter_start")
async def counter_start():
    global stop_event
    print("counter_start")
    stop_event.clear()  # Reset the stop event
    thread = threading.Thread(target=start_increment_counter, args=(100,))
    thread.start()
    return {"message": "Counter started in the background"}


@router.get("/counter_stop")
async def counter_stop():
    global stop_event
    stop_event.set()  # Signal the background task to stop
    return {"message": "Counter will stop soon"}


@router.get("/get_counter")
async def get_count():
    print("get_counter")
    global counter
    with counter_lock:
        current_counter = counter
    return {"counter": current_counter}


@router.get("/hello_stream")
async def hello_stream():
    def hello_stream_iter():
        data = {"aaa": "bbb"}
        yield f"0:{json.dumps(data)}"

    return StreamingResponse(
        hello_stream_iter(),
        media_type="text/event-stream",
    )


class HelloApiPublic(BaseModel):
    text: str


@router.get("/hello-api", response_model=HelloApiPublic)
async def hello_api():
    return HelloApiPublic(text="hello-text")
