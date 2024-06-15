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
    system_config = {"role": "system", "content": CHAT_ROLE}
    user_config = {"role": "user", "content": []}
    query = (f"Generate a detailed accessibility report for user according to the following results: {combined_results}.\n\n "
             f"In case you have recommendations to steps that need to be made in order to make the place more"
             f"accessible, write them as well. Write the report in Hebrew. Each title should be written with "
             f"### at the beginning, and each sub-title should be written with - ** before the sub-title "
             f"and ** after the sub-title. In the recommendations part, write ### before the part's title, "
             f"and each recommendation should be in two lines - the first one for the recommendation's title, "
             f"with - ** before it and ** after it, and the second one should be the recommendation's description, "
             f"without any symbol.")
    user_content = [{"type": "text", "text": query}]
    user_config["content"] = user_content
    messages = [system_config, user_config]
    response = client.chat.completions.create(model=model, messages=messages, temperature=0.0)
    return response.choices[0].message.content

# if __name__ == '__main__':
#     image_path1 = "db/our_class/door_1/1.jpg"
#     image_path2 = "db/our_class/door_1/2.jpg"
#     image_path3 = "db/our_class/door_1/3.jpg"
#     image_path4 = "db/our_class/door_1/4.jpg"
#     images = [encode_image(image_path1), encode_image(image_path2),
#               encode_image(image_path3), encode_image(image_path4)]
#     query = ("Can you tell me what is the size of the door (at least an estimation), "
#              "and if the entry for this business is accessible? Please give a short estimation at first if the business"
#              " is accessible, and afterwards add a detailed explanation")
#     print(ask_chat_gpt_with_images(query, images))
