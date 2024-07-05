import base64

from utils import encode_image
from utils import get_queries_dict
from chat_api import ask_chat_gpt_with_images, ask_chat_gpt_final_result, ask_chat_gpt_comment


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
    for query in queries:
        result = ask_chat_gpt_with_images(query, base64_images)
        results[query] = result

    return base64_images, results


def query_comment(place_result, comment_img, comment_text):
    comment_img_base64 = base64.b64encode(comment_img).decode('utf-8')
    comment_response = ask_chat_gpt_comment(place_result, comment_img_base64, comment_text)

    return comment_response


def query_final_result(results):
    # Combine all results into a single data structure, filter out non-existing places
    combined_results = "; ".join([f"{place}: {result}" for place, result in results.items() if 'המשתמש הצהיר' not in result])

    # Send the combined results to the ask_chat_gpt_final_result function
    final_result = ask_chat_gpt_final_result(combined_results)

    return final_result
