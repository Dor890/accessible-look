import base64

from utils import encode_image
from utils import get_queries_dict
from chat_api import ask_chat_gpt_place, ask_chat_gpt_final_result, ask_chat_gpt_comment
from claude_api import ask_claude_place, ask_claude_final_result, ask_claude_comment


def query_place(user, place):
    # Get the list of queries for the given place from queries_dict
    queries_dict = get_queries_dict()
    queries = queries_dict.get(place)

    # Import Image here to avoid circular import
    from models import Image

    # Get images uploaded by the user for the place from the database
    images = Image.query.filter_by(user_id=user.id, place=place).all()

    # Convert images to Base64
    base64_images = [encode_image(image.filepath) for image in images]

    # Get ChatGPT results for each query
    results = {}
    query_func = get_model_methods()["place"]
    for query in queries:
        result = query_func(query, base64_images)
        results[query] = result[0].text if type(result) is list else result

    return base64_images, results


def query_comment(place_result, comment_img, comment_text):
    comment_img_base64 = base64.b64encode(comment_img).decode('utf-8')
    query_func = get_model_methods()["comment"]
    comment_response = query_func(place_result, comment_img_base64, comment_text)

    return comment_response


def query_final_result(results):
    # Combine all results into a single data structure, filter out non-existing places
    combined_results = "; ".join([f"{place}: {result}" for place, result in results.items() if 'המשתמש הצהיר' not in result])

    query_func = get_model_methods()["final_result"]

    # Send the combined results to the ask_chat_gpt_final_result function
    final_result = query_func(combined_results)

    return final_result


def get_model_methods(ai_tool="CLAUDE"):
    if ai_tool not in ["GPT", "CLAUDE"]:
        # Set Chat-GPT as default AI tool
        ai_tool = "GPT"

    if ai_tool == "GPT":
        methods = {
            "place": ask_chat_gpt_place,
            "final_result": ask_chat_gpt_final_result,
            "comment": ask_chat_gpt_comment
        }
    elif ai_tool == "CLAUDE":
        methods = {
            "place": ask_claude_place,
            "final_result": ask_claude_final_result,
            "comment": ask_claude_comment
        }

    return methods
