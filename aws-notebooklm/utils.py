import regex as re
import jinja2
import json, os, sys, time, io
from pypdf import PdfReader
from pathlib import Path
import boto3
from pydub import AudioSegment
import tempfile

model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
host_name = "Amy"
audio_dir = ""

def set_audio_dir(dir_path):
    global audio_dir
    audio_dir = dir_path
    
def get_system_prompt(host_name):
    fs_loader = jinja2.FileSystemLoader(searchpath="templates")
    template_env = jinja2.Environment(loader=fs_loader)
    template = template_env.get_template("podcast_system.txt")
    system_prompt = template.render(host=host_name)
    return system_prompt


def cleanup(text):
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip()) # Remove newlines 
    text = re.sub(r"\n\s*\n", "\n\n", text)
    text = re.sub(r'[/X]', "", text)     #Remove hexadecimal chars
    text = re.sub(r"(\\u[0-9A-Fa-f]+)"," ",text) #Remove other speciail characters
    return text

def pdf_to_text(file_path):
    text = ""
    with Path(file_path).open("rb") as f:
        reader = PdfReader(f)
        text += "\n\n".join([page.extract_text() for page in reader.pages])
    return cleanup(text)

def uploaded_pdf(pdf_file):
    text= ""
    pdf_bytes = pdf_file.read()
    pdf_file = io.BytesIO(pdf_bytes)
    reader = PdfReader(pdf_file)
    text += "\n\n".join([page.extract_text() for page in reader.pages])
    return text

def generate_podcast_script(system_prompt,text):
    system_prompts = [{"text": system_prompt}]
    message_user = {
        "role": "user", "content": [{"text": text }]
    }
    message_assistant = {
        "role": "assistant", "content": [{"text": "{" }]
    }
    
    messages = [message_user,message_assistant]
    bedrock_client = boto3.client(service_name='bedrock-runtime')
    temperature = 0.5
    top_k = 200
    inference_config = {"temperature": temperature, 'maxTokens': 4096}     # Base inference parameters to use.
    additional_model_fields = {"top_k": top_k}     # Additional inference parameters to use.

    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields
    )
    json_text = "{" + response['output']['message']['content'][0]['text']
    response_json = json.loads(json_text,strict=False)
    extracted_speech = []
    i = 0
    for item in response_json['dialog']:
        i+= 1
        pos = item.find(":")
        speaker, speech = item[:pos].strip(), item[pos+1:].strip()
        extracted_speech.append({'speaker': speaker,
                            'speech':speech, 
                           })    
    guest_name = response_json["guest"]
    title = response_json["podcast_title"]
    return guest_name,title,extracted_speech

def generate_audio(voice_id,text,file_name):
    polly_client = boto3.Session().client('polly')
    response = polly_client.synthesize_speech(VoiceId=voice_id, OutputFormat='mp3', Text = text,Engine = 'generative',LanguageCode='en-US',TextType='ssml')
    file = open(file_name, 'wb')
    file.write(response['AudioStream'].read())
    file.close()
    return file_name

def generate_audio_files(guest_name,extracted_speech,pbar=None):
    global audio_dir
    if audio_dir == "":
        audio_dir = tempfile.TemporaryDirectory().name
    Path(audio_dir).mkdir(parents=True, exist_ok=True)

    speaker_voice = {guest_name:"Matthew",host_name:"Amy"}    
    sounds_files = []
    for i, af in enumerate(extracted_speech):
        file_name = f'{audio_dir}/audio_file_{i}.mp3'
        sounds_files.append(generate_audio(speaker_voice[af['speaker']],af['speech'],file_name))
        if pbar is not None:
            value = int((i+1)/len(extracted_speech) * 100)
            if value == 100:
                pbar.progress(value,"That's it. Final one.")
            elif value > 75:
                pbar.progress(value,"Almost there..")
            else:
                pbar.progress(value,"Generating audio files...")
 
    return sounds_files

def combine_files(title,sounds_files):
    combined = AudioSegment.empty()  
    silence = AudioSegment.silent(duration=500)

    for sf in sounds_files:
        combined += AudioSegment.from_file(sf,format="mp3") + silence

    file_handle = combined.export(f"{audio_dir}/{title}.mp3", format="mp3")
    return file_handle.name