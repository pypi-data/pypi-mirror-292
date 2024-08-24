
from PIL import Image

import requests
import os

class HugginFace:
    API_KEY = os.environ.get("HUGGINFACE_API_KEY")
    HEADERS = {"Authorization": f"Bearer {API_KEY}"}
    
    def __init__(self, api_url):
        self.api_url = api_url

    def __request(self, payload):
        response = requests.post(self.api_url, headers = self.HEADERS, json = payload)
        print(response.content)
        return response

    def request_image(self, payload):
        return self.__request(payload).content

    def request_json(self, payload):
        return self.__request(payload).json()
    
    def download_image(self, prompt, output_filename):
        """
        Makes a request with the provided payload and stores the image received as response
        in the local storage.

        This method must be used with image generation urls.
        """
        image_content = self.request_image(prompt)
        with open(output_filename, 'wb') as outfile:
            outfile.write(image_content)













# from PIL import Image

# import requests
# import os
# import io

# API_KEY = os.environ.get("HUGGINFACE_API_KEY")
# HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# """
# You go to any existing model in HugginFace platform, then click on 'Deploy' (on
# the right side) and 'Inference API' and there you have the url and the query
# structure.
# """

# def __request(api_url, payload):
#     response = requests.post(api_url, headers = HEADERS, json = payload)
#     print(response)
#     return response

# def __request_image(api_url, payload):
#     return __request(api_url, payload).content

# def __request_json(api_url, payload):
#     return __request(api_url, payload).json()

# def test_image():
#     #API_URL = 'https://api-inference.huggingface.co/models/stabilityai/stable-cascade'
#     #API_URL = 'https://api-inference.huggingface.co/models/stabilityai/stable-cascade-prior'
#     #API_URL = 'https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5'
#     #API_URL = 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1'
#     API_URL = 'https://api-inference.huggingface.co/models/prompthero/openjourney'

#     PAYLOAD = {
#         'inputs': 'Hiperrealistic monk between two cars in the middle of a city'
#     }

#     response = __request_image(API_URL, PAYLOAD)
#     Image.open(io.BytesIO(response)).save('test_tintin.png')

# def test_tintin():
#     API_URL = 'https://api-inference.huggingface.co/models/Pclanglais/TintinIA'

#     PAYLOAD = {
#         'inputs': 'Astronaut riding a horse and holding a coffee'
#     }

#     response = __request_image(API_URL, PAYLOAD)
#     Image.open(io.BytesIO(response)).save('test_tintin.png')

# def test_gemma():
#     API_URL = 'https://api-inference.huggingface.co/models/google/gemma-7b'

#     PAYLOAD = {
#         'inputs': '¿Cuántos habitantes tiene España?'
#     }

#     response = __request_json(API_URL, PAYLOAD)

#     print(response)

# def test():
#     API_URL = 'https://api-inference.huggingface.co/models/deepset/roberta-base-squad2'
    
#     PAYLOAD = {
#         'inputs': {
#             'question': 'What is my name?',
#             'context': 'My name is Clara and I live in Berkeley.',
#         }
#     }

#     response = __request_json(API_URL, PAYLOAD)
#     #response has, in this case, 'answer'
#     print(response)