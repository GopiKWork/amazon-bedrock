import pathlib
from PIL import Image as PILImage
import base64
import json, io, os
import boto3
import sagemaker
session = boto3.Session()
sagemaker_session = sagemaker.Session()
studio_region = sagemaker_session.boto_region_name 
bedrock = session.client("bedrock", region_name=studio_region)
br = session.client("bedrock-runtime", region_name=studio_region)
meta_llama_model_id = "us.meta.llama3-2-11b-instruct-v1:0"  
titan_embed_model_id = "amazon.titan-embed-image-v1"


def resize_img(b64imgstr, size=(256, 256)):
    buffer = io.BytesIO()
    img = base64.b64decode(b64imgstr)
    img = PILImage.open(io.BytesIO(img))

    rimg = img.resize(size, PILImage.LANCZOS)
    rimg.save(buffer, format=img.format)

    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def img2base64(image_path,resize=False):
    with open(image_path, "rb") as img_f:
        img_data = base64.b64encode(img_f.read())
    if resize:
        return resize_img(img_data.decode())
    else:
        return img_data.decode()

def get_image(image_path):
    with open(image_path, "rb") as img_f:
       return img_f.read()

def converse_meta_llama_multi(prompts, image_paths):
    text_prompts = []
    image_prompts = []
    for p in prompts:
        text_prompts.append( {"text": p})
    for ip in image_paths:
        ext = pathlib.Path(ip).suffix[1:]
        if ext == 'jpg':
            ext = 'jpeg' 
        image_data = get_image(ip)
        image_prompts.append({"image": {"format": f"{ext}","source": {"bytes": image_data}}})

    messages = [{"role": "user","content": [],}]
    messages[0]["content"].extend(text_prompts)
    messages[0]["content"].extend(image_prompts)

    inference_config={"maxTokens": 2048, "temperature": 1.0, "topP": 0.9}
    
    response = br.converse(
        modelId=meta_llama_model_id,
        messages=messages,
        inferenceConfig = inference_config
    )
    response_text = response["output"]["message"]["content"][0]["text"]
    return response_text


def converse_meta_llama(prompt, image_path=None):
    prompts = [prompt]
    image_paths = []
    if image_path:
        image_paths = [image_path]
    return converse_meta_llama_multi(prompts,image_paths)