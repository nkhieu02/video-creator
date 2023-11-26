from datetime import datetime

data = datetime.now().strftime('%B %d, %Y')

def scripting_form():
    return 'Scene {an integer number}\n'\
           'Image\Giphy: {Detail desription of the image or giphy you need}\n'\
           'Voiceover: {The text to voice out enclosed in ""}\n\n'

def generate_scripting_instruction(blog, target_audience, purpose):
    form = scripting_form()
    return f'Base on the blog below, write me a script for a short video with '\
           f'{purpose} purpose to young adults '\
           f'with a bit of focus on {target_audience}:\n\n{blog}\n\n'\
           f'The script should consist of multiple scenes such that '\
           f'each scene including the last one strictly follow this structure:\n{form}'

## Prompt 2: Get the caption
def generate_caption_instruction(script, platform):
    return f'Base on the video script below, write me a '\
           f'caption secifically for {platform}\n\n{script}'
