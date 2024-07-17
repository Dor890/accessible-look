from openai import OpenAI
from utils import get_queries_dict

client = OpenAI()

MODEL = 'gpt-4o'
CHAT_ROLE = 'You are an expert in accessibility who should validate if places are accessible according to photos.'


def ask_chat_gpt_place(query, images):
    system_config = {"role": "system", "content": CHAT_ROLE}
    user_config = {"role": "user", "content": []}
    user_content = [{"type": "text", "text": query}]
    for image in images:
        user_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image}"}})
    user_config["content"] = user_content
    messages = [system_config, user_config]
    response = client.chat.completions.create(model=MODEL, messages=messages, temperature=0.0)
    return response.choices[0].message.content


def ask_chat_gpt_final_result(combined_results):
    queries_dict = get_queries_dict()
    system_config = {"role": "system", "content": CHAT_ROLE}
    user_config = {"role": "user", "content": []}
    query = ''.join(queries_dict["final_result"]).format(combined_results)
    user_content = [{"type": "text", "text": query}]
    user_config["content"] = user_content
    messages = [system_config, user_config]
    response = client.chat.completions.create(model=MODEL, messages=messages, temperature=0.0)
    return response.choices[0].message.content


def ask_chat_gpt_comment(place_result, comment_img, comment_text):
    queries_dict = get_queries_dict()
    query = ''.join(queries_dict["comment"]).format(place_result, comment_text)
    system_config = {"role": "system", "content": CHAT_ROLE}
    user_config = {"role": "user", "content": []}
    user_content = [{"type": "text", "text": query}]
    user_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{comment_img}"}})
    user_config["content"] = user_content
    messages = [system_config, user_config]
    response = client.chat.completions.create(model=MODEL, messages=messages, temperature=0.0)
    return response.choices[0].message.content
