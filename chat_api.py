import base64

from openai import OpenAI

CHAT_ROLE = 'You are an assistant that should validate if places are accessible.'

client = OpenAI()
IMAGE_PATH1 = "db/our_class/door_1/1.jpg"
IMAGE_PATH2 = "db/our_class/door_1/2.jpg"
IMAGE_PATH3 = "db/our_class/door_1/3.jpg"
IMAGE_PATH4 = "db/our_class/door_1/4.jpg"


# Open the image file and encode it as a base64 string
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


response = client.chat.completions.create(
    model='gpt-4o',
    messages=[
        {"role": "system", "content": CHAT_ROLE},
        {"role": "user", "content": [
            {"type": "text", "text": "Can you tell me what is the size of the door (at least an estimation),"
                                     " and if the entry for this business is accessible?"},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{encode_image(IMAGE_PATH1)}"}
            },
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{encode_image(IMAGE_PATH2)}"}
            },
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{encode_image(IMAGE_PATH3)}"}
            },
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{encode_image(IMAGE_PATH4)}"}
            }
        ]}
    ],
    temperature=0.0,
)
print(response.choices[0].message.content)