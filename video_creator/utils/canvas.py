from huggingface_hub import AsyncInferenceClient
import requests
import os
from video_creator.master.functions import *
from video_creator.config.config import Config
import cv2
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import asyncio
import httpx

CONFIG = Config()
CLIENT = AsyncInferenceClient()

# Image to image.
# Should be used to set the color tone.
async def image_2_image(scene: int, 
                        image: str,
                        prompt: str,
                        cfg,
                        num_inference_steps=30,
                        socket=None):
    
    try:
        image = await CLIENT.image_to_image(image=image,
                                           prompt=prompt,
                                           model=cfg.image_2_image_model,
                                           num_inference_steps=num_inference_steps)
    except Exception as e:
        await stream_output(type='logs',
                      output=f'Failed to retrieve image due to error {e}',
                      websocket=socket)

    else:
        saving_path = os.path.join(cfg.compile_video_dir, f'scene_{scene}_image.png')
        image.save(saving_path)
        await stream_output(type='logs',
                      output=f'Image downloaded successfully and saved at {saving_path}',
                      websocket=socket)

# Text to image


async def text_2_image(scene: int, 
                       prompt: str,
                       cfg,
                       negative_prompt="low resolution, blurry",
                       num_inference_steps=30,
                       socket=None):
    await stream_output("logs", f"\n🔎 Generate image that fit the description: '{prompt}'...", socket)
    try:
        image = await CLIENT.text_to_image(prompt=prompt,
                                     negative_prompt=negative_prompt,
                                     model=cfg.text_2_image_model,
                                     num_inference_steps=num_inference_steps)
    except Exception as e:
        await stream_output(type='logs',
                      output=f'Failed to retrieve image due to error {e}',
                      websocket=socket)

    else:
        saving_path = os.path.join(cfg.compile_video_dir, f'scene_{scene}_image.png')
        image.save(saving_path)
        await stream_output(type='logs',
                      output=f'Image downloaded successfully and saved at {saving_path}',
                      websocket=socket)


# Text to voice

speakers = [
    {
      "id": "6ec4d93b-1f54-4420-91f8-33f188ee61f3",
      "name": "Gracie Wise"
    },
    {
      "id": "64b58ac0-54d1-4aae-8344-c52f3dfe2c9a",
      "name": "Zofija Kendrick"
    },
    {
      "id": "0f82817b-eea7-4f28-8a02-5900a1b23e30",
      "name": "Damien Black"
    },
    {
      "id": "d91d2f95-1a1d-4062-bad1-f1497bb5b487",
      "name": "Gitta Nikolina"
    },
    {
      "id": "b8ffb895-79b8-4ec6-be9c-6eb2d1fbe83c",
      "name": "Claribel Dervla"
    },
    {
      "id": "f05c5b91-7540-4b26-b534-e820d43065d1",
      "name": "Ana Florence"
    },
    {
      "id": "fc9917ef-8f32-418e-9254-e535c0c6df3d",
      "name": "Zacharie Aimilios"
    },
    {
      "id": "8f3b11ce-ed66-4752-a705-c05fe381a587",
      "name": "Szofi Granger"
    },
    {
      "id": "81bad083-72dc-4071-8548-70ba944b8039",
      "name": "Andrew Chipper"
    },
    {
      "id": "71c6c3eb-98ca-4a05-8d6b-f8c2b5f9f3a3",
      "name": "Narelle Moon"
    }
  ]

async def download_audio(audio_url: str, save_path: str, socket=None):
    response = requests.get(audio_url)

    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        await stream_output(type="logs",
                      output=f"Audio downloaded successfully and saved at {save_path}",
                      websocket=socket)
    else:
        await stream_output(type="logs",
                      output=f"Failed to download audio. Status code: {response.status_code}",
                      websocket=socket)


import json
async def text_2_voice(scene: int,
                       text: str,
                       cfg,
                       voice_id: str = "71c6c3eb-98ca-4a05-8d6b-f8c2b5f9f3a3",
                       emotion: str = 'Happy', 
                       name: str = None,
                       speed= 1.5, 
                       socket=None):
    '''
    emotion

    Neutral - Neutral
    Happy - Happy
    Sad - Sad
    Surprise - Surprise
    Angry - Angry
    Dull - Dull

    '''
    await stream_output("logs", f"\n🔎 Generate voice over for: '{text}'...", socket)
    url = "https://app.coqui.ai/api/v2/samples"
    API = os.getenv('COQUI_API')
    headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {API}"
    }
    payload = {"voice_id": voice_id, "text": text, "emotion": emotion, 
               "name": name, "speed": speed}
    payload = {key: value for key, value in payload.items() \
               if value is not None}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

    audio_url = json.loads(response.text)["audio_url"]
    saving_path = os.path.join(cfg.compile_video_dir, f'scene_{scene}_voice.wav')
    await download_audio(audio_url=audio_url, 
                   save_path=saving_path,
                   socket=socket)

async def texts_2_images_voices(scenes, cfg, socket):
    tasks_voices = [text_2_voice(scene=i, text=scene['voice'], cfg=cfg, socket=socket) \
             for i, scene in enumerate(scenes)]
    tasks_images = [text_2_image(scene=i, prompt=scene['image'], cfg=cfg, socket=socket) \
             for i, scene in enumerate(scenes)]
    tasks = tasks_voices + tasks_images
    await asyncio.gather(*tasks)    


# Function to create a video from images
def images_to_video(image_paths, output_video_path, fps):
    img = cv2.imread(image_paths[0])
    height, width, layers = img.shape

    # Create a VideoWriter object
    video = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for image_path in image_paths:
        img = cv2.imread(image_path)
        video.write(img)

    cv2.destroyAllWindows()
    video.release()

# Function to combine video and audio
def combine_video_audio(video_path, audio_path, output_path):
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    # Set the audio of the video clip to the provided audio clip
    video_clip = video_clip.set_audio(audio_clip)

    # Write the final video with audio
    video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')


def compile_video():
    
    compile_dir = CONFIG.compile_video_dir
    # Example usage
    image_paths = [x for x in os.listdir(compile_dir) if 'png' in x] 
    audio_paths = [x for x in os.listdir(compile_dir) if 'wav' in x] 
    if len(image_paths) != len(audio_paths):
        raise ValueError("Error: The number of image paths and audio paths is not equal.")

    image_paths = [os.path.join(compile_dir, x) for x in image_paths]
    audio_paths = [os.path.join(compile_dir, x) for x in audio_paths]
    output_video_path = os.path.join(CONFIG.compile_video_dir, 'output_video.mp4')
    fps = 50  # Frames per second
    
    # Create individual videos for each image and audio pair
    for i in range(len(image_paths)):
        temp_output_video_path = os.path.join(compile_dir, f'temp_video_{i}.mp4')
        images_to_video([image_paths[i]], temp_output_video_path, fps)
        combine_video_audio(temp_output_video_path, audio_paths[i], os.path.join(compile_dir, f'temp_output_{i}.mp4'))
    
    # Concatenate the individual videos into a final video
    final_clips = [VideoFileClip(os.path.join(compile_dir,f'temp_output_{i}.mp4') )for i in range(len(image_paths))]
    final_clip = concatenate_videoclips(final_clips, method="compose")
    final_clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
    
    # Clean up temporary files
    for i in range(len(image_paths)):
        temp_output_video_path = os.path.join(compile_dir,f'temp_video_{i}.mp4')
        temp_output_path = os.path.join(compile_dir, f'temp_output_{i}.mp4')
        os.remove(temp_output_video_path)
        os.remove(temp_output_path)

    return output_video_path


