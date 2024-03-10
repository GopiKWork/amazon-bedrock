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
claude_sonnet_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
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


def invoke_claude_sonnet_multi(prompts, image_paths):
    text_prompts = []
    image_prompts = []
    for p in prompts:
        text_prompts.append( {"type": "text", "text": p})
    for ip in image_paths:
        ext = pathlib.Path(ip).suffix[1:]
        if ext == 'jpg':
            ext = 'jpeg' #Validation
        base64_string = img2base64(ip)
        image_prompts.append({"type": "image", "source": {"type": "base64","media_type": f"image/{ext}","data": base64_string}})

    body = json.dumps({"anthropic_version": "bedrock-2023-05-31","max_tokens": 4096, "temperature": 1.0, "messages": [ {"role": "user", "content": text_prompts + image_prompts}]})
    accept = "application/json"
    contentType = "application/json"
    response = br.invoke_model(
        body=body, modelId=claude_sonnet_model_id, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())
    return response_body.get("content")[0]["text"]


def invoke_claude_sonnet(prompt, image_path=None):
    prompts = [prompt]
    image_paths = []
    if image_path:
        image_paths = [image_path]
    return invoke_claude_sonnet_multi(prompts,image_paths)