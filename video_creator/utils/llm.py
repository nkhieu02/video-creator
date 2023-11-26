# libraries
from __future__ import annotations
from fastapi import WebSocket
from langchain.adapters import openai as lc_openai
from colorama import Fore, Style
from typing import Optional


async def create_chat_completion(
        messages: list,  # type: ignore
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        llm_provider: Optional[str] = None,
        stream: Optional[bool] = False,
        websocket: WebSocket | None = None,
) -> str:
    """Create a chat completion using the OpenAI API
    Args:
        messages (list[dict[str, str]]): The messages to send to the chat completion
        model (str, optional): The model to use. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.9.
        max_tokens (int, optional): The max tokens to use. Defaults to None.
        stream (bool, optional): Whether to stream the response. Defaults to False.
        llm_provider (str, optional): The LLM Provider to use.
        webocket (WebSocket): The websocket used in the currect request
    Returns:
        str: The response from the chat completion
    """

    # validate input
    if model is None:
        raise ValueError("Model cannot be None")
    if max_tokens is not None and max_tokens > 8001:
        raise ValueError(f"Max tokens cannot be more than 8001, but got {max_tokens}")

    # create response
    for attempt in range(10):  # maximum of 10 attempts
        response = await send_chat_completion_request(
            messages, model, temperature, max_tokens, stream, llm_provider, websocket
        )
        return response

    logging.error("Failed to get response from OpenAI API")
    raise RuntimeError("Failed to get response from OpenAI API")


import logging


async def send_chat_completion_request(
        messages, model, temperature, max_tokens, stream, llm_provider, websocket
):
    if not stream:
        result = lc_openai.ChatCompletion.create(
            model=model,  # Change model here to use different models
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            provider=llm_provider,  # Change provider here to use a different API
        )
        return result["choices"][0]["message"]["content"]
    else:
        return await stream_response(model, messages, temperature, max_tokens, llm_provider, websocket)


async def stream_response(model, messages, temperature, max_tokens, llm_provider, websocket=None):
    paragraph = ""
    response = ""

    for chunk in lc_openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            provider=llm_provider,
            stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            response += content
            paragraph += content
            if "\n" in paragraph:
                if websocket is not None:
                    await websocket.send_json({"type": "report", "output": paragraph})
                else:
                    print(f"{Fore.GREEN}{paragraph}{Style.RESET_ALL}")
                paragraph = ""
    return response


