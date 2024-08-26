import requests
import random
from typing import Union

def get_random_image(number=1, tag: Union[str, tuple, list] = None, rating: Union[str, tuple, list] = None, ignore = False):
    """Gets a random image from API that matches the specified tag(s) and/or rating(s)"""
    if number > 100:
        raise ValueError("The number of images requested is too high. Please request 100 or fewer images.") 
    
    response = requests.get("https://www.catgirlnexus.xyz/api/references/all_tags.json").json()
    filtered_urls = []
    
    # Normalize tag and rating inputs to lists for easier handling
    if isinstance(tag, str):
        tag = [tag]
    if isinstance(rating, str):
        rating = [rating]
    
    # Iterate over the dictionary items
    for url, attributes in response.items():
        image_tags = list(attributes.keys())
        image_rating = attributes.get("rating", "")
        
        # Check if the image matches the given tag(s)
        tag_match = True if not tag else any(t in image_tags for t in tag)
        
        # Check if the image matches the given rating(s)
        rating_match = True if not rating else image_rating in rating
        
        # Append URL if both conditions are met
        if tag_match and rating_match:
            filtered_urls.append(url)
        
        # Stop if we've collected enough URLs
        if len(filtered_urls) >= number:
            break
    
    returnvalue = random.sample(filtered_urls, min(len(filtered_urls), number)) if filtered_urls else []

    if (returnvalue == [] or len(returnvalue) != number) and ignore == False:
        print("Warning! The API didn't contain enough images to fit your request. You may contact _.lex0 on Discord to submit if you want more images in the specific tags.\nTo remove this warning insert `ignore=True` in the function")

    return random.sample(filtered_urls, min(len(filtered_urls), number)) if filtered_urls else []

"""
# Example usage
print(get_random_image(number=5, tag="yuri", rating="safe"))
"""