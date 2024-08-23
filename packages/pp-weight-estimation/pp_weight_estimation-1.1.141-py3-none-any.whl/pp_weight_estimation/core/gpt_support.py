# We will use the OpenAI API to get the result of the image

import base64
import requests

__all__ = ['get_gpt_result','encode_image','get_count','get_gpt_result2','multi_ref_prompt']

prompt = "Count the number of {item} in the image and just return the number"
#gpt_prompt = f"Based on the reference image of weight {food_item_label} : {reference_image_gt}, what is the weight of the 2nd image? Please respond only in the format 'result : amount'."


# OpenAI API Key
api_key = None

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_gpt_result(image_path ,ref_image_path, api_key,prompt=prompt,detail="high"):
    # Getting the base64 string
    base64_image = encode_image(image_path)
    ref_base64_image = encode_image(ref_image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"}

    payload = {
    "model": "gpt-4o",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{ref_base64_image}",
                 "detail": detail
            }
            },
            {            
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                 "detail": detail
            }
            },
        ]
        }
    ],
    "max_tokens": 300}

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())
    return response


def get_gpt_result2(image_path , api_key,prompt=prompt,detail="high"):
    # Getting the base64 string
    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"}

    payload = {
    "model": "gpt-4o",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail" : detail
            }
            },
        ]
        }
    ],
    "max_tokens": 300}

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())
    return response

def get_count(response):
    try :
        result = float(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(e)
        result = False
    return result

def multi_ref_prompt(image_path, ref_image_list, api_key=None,prompt='test',detail="high"):
    """
    Multiple reference images in list format
    Args:
        image_path : str : Path to the image
        ref_image_list : list : List of reference images
        api_key : str : OpenAI API Key
        prompt : str : Prompt to be used
        detail : str : Detail of the image
    Returns:
        response : dict : Response from the API
    """

    base64_image = encode_image(image_path)
    if isinstance(ref_image_list, list):
        ref_base64_images = [encode_image(ref_image) for ref_image in ref_image_list]
    else:
        ref_base64_images = encode_image(ref_image_list)

    image_dict_data = [{"type": "text","text": prompt},
                       {"type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}",
                                      "detail": detail}
                        }]
    for i in range(len(ref_base64_images)):
        image_dict_data.append({"type":"image_url", 
                                "image_url":{"url":f"data:image/jpeg;base64,{ref_base64_images[i]}", 
                                             "detail": detail}})

    message_with_images = {"role": "user","content": image_dict_data }
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        message_with_images
        ]
    data = {
        "messages": messages,
        "model" : "gpt-4o",
        "temperature": 0.2
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"}
    
    response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
    print(response)
    print(response.text)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return False