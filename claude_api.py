import anthropic
from utils import get_queries_dict

client = anthropic.Anthropic()  # ANTHROPIC_API_KEY

MODEL = "claude-3-5-sonnet-20240620"
SYSTEM = "You are an expert in accessibility who should validate if places are accessible according to photos."

MAX_TOKENS = 4096


def ask_claude_place(query, images):
    messages = [{"role": "user", "content": []}]
    for image in images:
        messages[0]["content"].append({"type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": image
                                    }})
    messages[0]["content"].append({"type": "text", "text": query})
    response = client.messages.create(max_tokens=MAX_TOKENS, model=MODEL, temperature=0, system=SYSTEM,
                                      messages=messages)
    return response.content


def ask_claude_final_result(combined_results):
    queries_dict = get_queries_dict()
    messages = [{"role": "user", "content": []}]
    query = ''.join(queries_dict["final_result"]).format(combined_results)
    messages[0]["content"].append({"type": "text", "text": query})
    response = client.messages.create(max_tokens=MAX_TOKENS, model=MODEL, temperature=0, system=SYSTEM,
                                      messages=messages)
    return response.content[0].text


def ask_claude_comment(place_result, comment_img, comment_text):
    queries_dict = get_queries_dict()
    messages = [{"role": "user", "content": []}]
    query = ''.join(queries_dict["comment"]).format(place_result, comment_text)
    messages[0]["content"].append({"type": "text", "text": query})
    messages[0]["content"].append({"type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": comment_img
                                }})
    response = client.messages.create(max_tokens=MAX_TOKENS, model=MODEL, temperature=0, system=SYSTEM,
                                      messages=messages)
    return response.content
