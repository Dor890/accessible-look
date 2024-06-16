import base64

from openai import OpenAI
from utils import get_queries_dict


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


def ask_chat_gpt_generate_report(user_id, places):
    model = 'gpt-4o'
    system_config = {"role": "system", "content": CHAT_ROLE}
    user_config = {"role": "user", "content": []}
    query = f"Generate a detailed accessibility report for user {user_id} covering the following places: {', '.join(places)}."
    user_content = [{"type": "text", "text": query}]
    user_config["content"] = user_content
    messages = [system_config, user_config]
    response = client.chat.completions.create(model=model, messages=messages, temperature=0.0)
    return response.choices[0].message.content


def ask_chat_gpt_final_result(combined_results):
    model = 'gpt-4o'
    queries_dict = get_queries_dict()
    system_config = {"role": "system", "content": CHAT_ROLE}
    user_config = {"role": "user", "content": []}
    query = ''.join(queries_dict["final_result"]).format(combined_results)
    user_content = [{"type": "text", "text": query}]
    user_config["content"] = user_content
    messages = [system_config, user_config]
    response = client.chat.completions.create(model=model, messages=messages, temperature=0.0)
    return response.choices[0].message.content
