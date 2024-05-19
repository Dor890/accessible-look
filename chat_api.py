import os
import json
import base64

from openai import OpenAI

CHAT_ROLE = 'You are an assistant that should validate if places are accessible.'
API_KEY = ''


client = OpenAI(api_key=API_KEY,)


def convert_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def ask_openai_with_image(query, image_path):
    image_base64 = convert_image_to_base64(image_path)

    prompt = f"{query}\n\nImage (base64-encoded): {image_base64}"

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_path,
                        },
                    }
                ],
            }
        ],
        max_tokens=300,
    )
    print(completion.choices[0].text)
    print(dict(completion).get('usage'))
    print(completion.model_dump_json(indent=2))
    return completion.choices[0].message['content']


door_query = "Can you tell me what is the size of the door, and if the entry for this business is accessible?"
image_path = "./db/our_class/door_1/1.jpg"

response = ask_openai_with_image(door_query, image_path)
print(response)

