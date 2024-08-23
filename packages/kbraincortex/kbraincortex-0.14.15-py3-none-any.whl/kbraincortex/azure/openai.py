from typing import Optional, Callable
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.settings.configuration import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT
from app.logging.system import log_info

def get_llm(
    azure_deployment:str='gpt-4o', 
    api_version:str='2024-06-01', 
    temperature:int=0, 
    max_tokens:Optional[int]=None, 
    timeout:Optional[int]=None, 
    max_retries:Optional[int]=1, 
    streaming:bool=False, 
    api_key:str=AZURE_OPENAI_API_KEY, 
    azure_endpoint:str=AZURE_OPENAI_ENDPOINT
) -> AzureChatOpenAI:
    llm = AzureChatOpenAI(
        azure_deployment=azure_deployment,
        api_version=api_version,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries,
        streaming=streaming,
        api_key=api_key,
    )
    return llm


def prepare_message_list(
    system_prompt:str,
    messages:list
):
    message_list = [
        (
            "system",
            system_prompt
        )
    ]
    for message in messages:
        if message["role"] == "user":
            message_list.append(
                (
                    "human",
                    message["content"]
                )
            )
        if message["role"] == "assistant":
            message_list.append(
                (
                    "ai",
                    message["content"]
                )
            )
    return message_list

def setup_prompt_chain(
    system_prompt:str,
    messages:list=[],
    **kwargs
) -> ChatPromptTemplate:
    
    llm = get_llm(**kwargs)
    message_list = prepare_message_list(system_prompt, messages)
    prompt = ChatPromptTemplate.from_messages(message_list)
    chain = prompt | llm
    return chain 

def stream_llm_output(
    system_prompt:str,
    messages:list,
    streaming_function:Callable,
    parameters:Optional[dict] = {},
    streaming_args:dict = {},
    content_key:str = "message",
    **kwargs
):
    chain = setup_prompt_chain(system_prompt, messages, **kwargs)
    response = ""
    
    
    streaming_args[content_key] = ""
    streaming_args["type"] = "chat_response"
    streaming_args["status"] = "streaming"
    streaming_function(**streaming_args)
    
    for chunk in chain.stream(parameters):
        log_info(f"Streaming chunk: {chunk}")
        streaming_args[content_key] = chunk.content
        streaming_args["type"] = "chat_response"
        streaming_args["status"] = "streaming"
        streaming_function(**streaming_args)
        response += chunk.content

    streaming_args[content_key] = ""
    streaming_args["type"] = "chat_response"
    streaming_args["status"] = "completed"
    streaming_function(**streaming_args)

    return response

def sync_llm_output(
    system_prompt:str,
    messages:list,
    parameters:Optional[dict] = {},
    **kwargs
):
    chain = setup_prompt_chain(system_prompt, messages, **kwargs)
    response = chain.invoke(parameters)
    return response.content