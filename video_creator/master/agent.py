from video_creator.config import Config
from video_creator.master.functions import *
from video_creator.utils.canvas import *
import time

class GPTResearcher:
    """
    GPT Researcher
    """
    def __init__(self, blog, purpose, platform , target_audience, 
                 config_path=None, websocket=None):
        """
        Initialize the GPT Researcher class.
        Args:
            blog:
            report_type:
            config_path:
            websocket:
        """
        self.blog = blog
        self.purpose = purpose
        self.target_audience =target_audience
        self.platform = platform
        self.cfg = Config(config_path)
        self.websocket = websocket

    async def run(self):
        """
        Runs the GPT Researcher
        Returns:
            Report
        """
        print(f"🔎 Creating {self.purpose} video script targetting {self.target_audience}...")
        # Generate script:
        script = await generate_script(self.blog, self.target_audience,
                                       self.purpose, self.cfg)
        await stream_output("logs", script, self.websocket)

        # Extract scene components
        scenes = await extract_scene_components(script, socket=self.websocket)
        await stream_output("logs",
                            f"🧠 I will generate image and voice for these scenes {scenes}...",
                            self.websocket)

        # Create image each scene
        for i, scene in enumerate(scenes):
            await text_2_image(scene=i, 
                               prompt=scene['image'], 
                               socket=self.websocket,
                               cfg=self.cfg)
            await text_2_voice(scene=i,
                               text=scene['voice'], 
                               emotion='Happy', 
                               socket=self.websocket,
                               cfg=self.cfg)
            
        # await texts_2_images_voices(scenes=scenes, cfg= self.cfg, socket=self.websocket)

        # Compile video
        await stream_output("logs", f"✍️ Compile components into a video", self.websocket)
        video_path = compile_video()

        # Generate caption
        caption = await generate_caption(script=script, platform=self.platform, cfg=self.cfg)
        await stream_output("logs", f"Copy this caption designed for {self.platform}: '{caption}'", self.websocket)

        time.sleep(2)
        return video_path


