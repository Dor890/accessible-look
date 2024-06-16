from utils import get_queries_dict
from chat_api import ask_chat_gpt_with_images, ask_chat_gpt_final_result
from utils import encode_image


def query_place(user, place):
    # Get the list of queries for the given place from queries_dict
    queries_dict = get_queries_dict()
    queries = queries_dict.get(place)

    if queries is None:
        print(f"No queries found for place: {place}")
        return [], "No queries found"

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


def query_final_result(results):
    # Combine all results into a single data structure
    combined_results = "; ".join([f"{place}: {result}" for place, result in results.items()])

    # Send the combined results to the ask_chat_gpt_final_result function
    final_result = ask_chat_gpt_final_result(combined_results)

    return final_result
