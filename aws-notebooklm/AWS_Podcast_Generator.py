import streamlit as st
import json
from io import StringIO
import uuid
import sys
import os
import tempfile as tmp
from utils import *


st.set_page_config(page_title="Amazon Bedrock Podcast generator", layout="wide")
st.header("Generate Podcast with Amazon Bedrock from any pdf")
st.markdown('''
You can upload a PDF file and generate a podcast, sitback and listen. 
Works with any pdf file. 
Try now.
'''
)
st.image("images/podcast_studio.jpeg",width=400)
st.markdown('---')


pdf_file = st.file_uploader(f"Select file to upload",type='pdf', accept_multiple_files=False)
if not pdf_file:
    st.info("Please upload PDF documents to continue.")
    st.stop()
else:
    text = uploaded_pdf(pdf_file)
    system_prompt = get_system_prompt(host_name)
    with st.status("Generating transcript.."):
        guest_name,title,extracted_speech = generate_podcast_script(system_prompt,text)
    
    transcript = '\n'.join(af['speech'] for af in extracted_speech)
    with st.expander("Podcast transcript"):
        st.write(transcript)

    pbar = st.progress(0, text="Generating audio files...")
    sfiles = generate_audio_files(guest_name,extracted_speech,pbar)
    podcast_file = combine_files(title,sfiles)
    st.write("Listen to podcast")
    st.audio(podcast_file, format="audio/mp3", loop=False)
