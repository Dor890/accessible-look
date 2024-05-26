import base64

from openai import OpenAI

CHAT_ROLE = 'You are an assistant that should validate if places are accessible.'

client = OpenAI()


# Open the image file and encode it as a base64 string
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def ask_chat_gpt_with_images(query, images):
    model = 'gpt-4o'
    system_config = {"role": "system", "content": CHAT_ROLE}
    user_config = {"role": "user", "content": []}
    user_content = [{"type": "text", "text": query}]
    for image in images:
        user_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image}"}})
    user_config["content"] = user_content
    messages = [system_config, user_config]
    response = client.chat.completions.create(model=model, messages=messages, temperature=0.0)
    return response.choices[0].message.content


if __name__ == '__main__':
    image_path1 = "db/our_class/door_1/1.jpg"
    image_path2 = "db/our_class/door_1/2.jpg"
    image_path3 = "db/our_class/door_1/3.jpg"
    image_path4 = "db/our_class/door_1/4.jpg"
    images = [encode_image(image_path1), encode_image(image_path2),
              encode_image(image_path3), encode_image(image_path4)]
    query = ("Can you tell me what is the size of the door (at least an estimation), "
             "and if the entry for this business is accessible?")
    print(ask_chat_gpt_with_images(query, images))
