from video_creator.utils.llm import *
from video_creator.master.prompts import *

async def generate_script(blog, target_audience, purpose, cfg):
    script_instruction = generate_scripting_instruction(blog=blog, target_audience=target_audience,
                                                        purpose=purpose)
    messages = []
    messages.append({'role': 'system', 'content': 'You are a professional advertising video script writer'})
    messages.append({'role': 'user', 'content': script_instruction})
    script = await create_chat_completion(
        messages=messages,
        model=cfg.smart_llm_model,
        llm_provider=cfg.llm_provider,
    )
    return script

async def generate_caption(script: str, platform, cfg):
    caption_instruction = generate_caption_instruction(script=script, platform=platform)
    messages = []
    messages.append({'role': 'user', 'content': caption_instruction})
    script = await create_chat_completion(
        messages=messages,
        model=cfg.smart_llm_model,
        llm_provider=cfg.llm_provider,
    )
    return script

async def stream_output(type, output, websocket=None, logging=True):
    """
    Streams output to the websocket
    Args:
        type:
        output:

    Returns:
        None
    """
    if not websocket or logging:
        print(output)

    if websocket:
        await websocket.send_json({"type": type, "output": output})


import re

async def extract_scene_components(script, socket=None):
    
    images = []
    voices = []
    image_pattern = r'^Image[^:]+:'
    voice_pattern = r'^Voice[^:]+'
    lines = script.split('\n')
    for line in lines:
        if re.match(image_pattern, line):
            descrption = re.sub(r'^"|"$', '',line.split(':')[1].strip())
            images.append(descrption)
        if re.match(voice_pattern, line):
            descrption = re.sub(r'^"|"$', '',line.split(':')[1].strip())
            voices.append(descrption)
    if len(images) != len(voices):
        raise ValueError('Parsing error')
    scenes = [{'image': image, 'voice': voice} for \
              image, voice in zip(images, voices)]
    await stream_output("logs", f'Finnish parsing the script',socket)
    return scenes
