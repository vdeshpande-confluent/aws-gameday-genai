class Prompt(object):
    def __init__(self, prompt_id, text, image_url, session_id):
        self.prompt_id = prompt_id
        self.text = text
        self.image_url = image_url
        self.session_id = session_id