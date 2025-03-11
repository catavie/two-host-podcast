from google.cloud import texttospeech
from google import genai
from google.genai import types

#pip3 install google-cloud-secret-manager    
from google.cloud import secretmanager 

 
from typing import Sequence
import streamlit as st

import pandas as pd
import time
from PIL import Image, ImageOps
import os

# Load Google logo for background
@st.cache_resource
def load_google_logo():
    logo_path = '/path/to/your/logo/google_gemini_logo.png'
    if os.path.exists(logo_path):
        return Image.open(logo_path)
    return None


# get the API key from a secret manager entry
def access_secret_version(project_id, secret_id, version_id="latest"):
    """
    Access the payload for the given secret version if one exists.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Replace with your actual project ID and secret ID
project_id = "PROJECT_ID"
# change this to match your key 
secret_id = "SECRET_NAME_FOR_GEMINI_API_KEY"

api_key_value = access_secret_version(project_id, secret_id)

# set the model variable
#genai.configure()
ai_client = genai.Client(api_key=api_key_value)
ai_model='gemini-2.0-flash'



# Instantiates a client
# client = texttospeech.TextToSpeechClient()
def list_voices(language_code=None):
    client = texttospeech.TextToSpeechClient()
    response = client.list_voices(language_code=language_code)
    voices = sorted(response.voices, key=lambda voice: voice.name)

    print(f" Voices: {len(voices)} ".center(60, "-"))
    for voice in voices:
        languages = ", ".join(voice.language_codes)
        name = voice.name
        gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
        rate = voice.natural_sample_rate_hertz
        print(f"{languages:<8} | {name:<24} | {gender:<8} | {rate:,} Hz")

def list_voices_simple(language_code=None, selected_gender=None):
    client = texttospeech.TextToSpeechClient()
    response = client.list_voices(language_code=language_code)
    voices = sorted(response.voices, key=lambda voice: voice.name)
    
    df = pd.DataFrame(columns=['Languages', 'Name', 'Gender', 'Rate'])
    
    for voice in voices:
        languages = ", ".join(voice.language_codes)
        name = voice.name
        gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
        rate = voice.natural_sample_rate_hertz 

        df = pd.concat([df, pd.DataFrame([{'Languages': languages, 'Name': name, 'Gender': gender, 'Rate': rate}])], ignore_index=True)
               
    filtered_df= df.loc[df['Gender'] == selected_gender]
    
    return filtered_df['Name']
    

def unique_languages_from_voices(voices: Sequence[texttospeech.Voice]):
    language_set = set()
    for voice in voices:
        for language_code in voice.language_codes:
            language_set.add(language_code)
    return language_set


def list_languages():
    client = texttospeech.TextToSpeechClient()
    response = client.list_voices()
    languages = unique_languages_from_voices(response.voices)

    print(f" Languages: {len(languages)} ".center(60, "-"))
    for i, language in enumerate(sorted(languages)):
        print(f"{language:>10}", end="\n" if i % 5 == 4 else "")

def list_languages_simple():
    client = texttospeech.TextToSpeechClient()
    response = client.list_voices()
    languages = unique_languages_from_voices(response.voices)

    return sorted(languages)

def num_languages():
    client = texttospeech.TextToSpeechClient()
    response = client.list_voices()
    languages = unique_languages_from_voices(response.voices)
    return len(languages)
   
st.set_page_config(layout="wide", page_title="Two Hosts Podcast Generation with Google Gemini")

# Add Google logo as background
google_logo = load_google_logo()
if google_logo:
    # Resize the logo
    logo_width, logo_height = google_logo.size
    new_height = 70
    new_width = int((new_height / logo_height) * logo_width)
    google_logo = google_logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
    st.image(google_logo)

st.title("Two Hosts Podcast Generation with Google Gemini")

# organize the logic a bit
#####################################################
tab1, tab2, tab3 = st.tabs(["Language & Voices", "Add Podcast Content", "Podcast Script & Audio"])

with tab1:

    #lang_list = st.radio("Pick a language", list_languages_simple(), index=15, horizontal=True)
    lang_list = st.pills("Pick a language", options=list_languages_simple(), selection_mode="single", default="en-US")
    
    selected_lang = lang_list

    st.write("Total number of languages: ", num_languages())
    st.write("Selected language: ", selected_lang)

    #voices
    col1, col2 = st.columns(2)

    with col1:
        voice1gender = st.select_slider("First voice:", options= ["MALE", "FEMALE"])
        voice1 = st.selectbox("Pick the first voice id", list_voices_simple(selected_lang, voice1gender))
    
    with col2:
        voice2gender = st.select_slider("Second voice:", options= ["FEMALE", "MALE"])
        voice2 = st.selectbox("Pick the second voice id", list_voices_simple(selected_lang, voice2gender))
    
    on1 = st.toggle("Second: Add Podcast Content", value=True, disabled=True)
    on2 = False
    on3 = False


with tab2:
    if on1:
        #with st.form("my_tab2"):
        #68 is 2 lines
    
        article_txt = st.text_area("Paste a news article/content here... ", height=68*4)
        st.write(f"There are {len(article_txt)} characters.")
        
        on2 = st.toggle("Next: Inspect Podcast Script & Generate Audio")
            # submitted = st.form_submit_button("OK")
###################################
# or system instructions
# change the names of the voices here to make them have cultural affinity 
def assign_voice_names(v1gender="MALE", v2gender="FEMALE"):
    """Assigns voice names based on gender combinations.

    Args:
        voice1gender: Gender of the first voice ("MALE" or "FEMALE").
        voice2gender: Gender of the second voice ("MALE" or "FEMALE").

    Returns:
        A tuple containing the names for voice1 and voice2.
    """

    if v1gender == "MALE":
        if v2gender == "FEMALE":
            return "Liam", "Maya"
        else:  # v2gender == "MALE"
            return "Liam", "Tony"
    else:  # v1gender == "FEMALE"
        if v2gender == "MALE":
            return "Maya", "Liam"
        else:  # v2gender == "FEMALE"
            return "Maya", "Tina"

# assign names to voice genders
voice1Name, voice2Name = assign_voice_names(v1gender=voice1gender, v2gender=voice2gender)
############################################

def create_podcast(text, filename="podcast.mp3", v1Name="Liam", v2Name="Maya", v1Gender="MALE", v2Gender="FEMALE"):
    """
    Creates a podcast MP3/LINEAR16 file from the given text, with two voices (Liam and Maya).

    Args:
        text: The podcast script as a string.
        filename: The desired output filename (default: "podcast.mp3").
        v1Name: The name of the first voice (default: "Liam").
        v2Name: The name of the second voice (default: "Maya").
        v1Gender: The gender of the first voice ("MALE" or "FEMALE")
        v2Gender: The gender of the second voice ("MALE" or "FEMALE")

    Returns:
        audio file saved as mp3
    """

    client = texttospeech.TextToSpeechClient()

    # Build 3 voices for the request, select the language code ("en-US") and the ssml

    if v1Gender == "MALE":
        if v2Gender == "FEMALE":  
            male_voice_id = texttospeech.VoiceSelectionParams(
                language_code=selected_lang, ssml_gender=texttospeech.SsmlVoiceGender.MALE, name=voice1
                )

            female_voice_id = texttospeech.VoiceSelectionParams(
                language_code=selected_lang, ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, name=voice2
                )
        else: #  v2Gender = MALE
            male_voice_id = texttospeech.VoiceSelectionParams(
                language_code=selected_lang, ssml_gender=texttospeech.SsmlVoiceGender.MALE, name=voice1
                )

            female_voice_id = texttospeech.VoiceSelectionParams(
                language_code=selected_lang, ssml_gender=texttospeech.SsmlVoiceGender.MALE, name=voice2
                )
    else: #v1Gender is FEMALE
        if v2Gender == "FEMALE":  
            male_voice_id = texttospeech.VoiceSelectionParams(
                language_code=selected_lang, ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, name=voice1
                )

            female_voice_id = texttospeech.VoiceSelectionParams(
                language_code=selected_lang, ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, name=voice2
                )
        else: #v2Gender is MALE
            male_voice_id = texttospeech.VoiceSelectionParams(
                language_code=selected_lang, ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, name=voice1
                )

            female_voice_id = texttospeech.VoiceSelectionParams(
                language_code=selected_lang, ssml_gender=texttospeech.SsmlVoiceGender.MALE, name=voice2
                )


    # voice gender ("neutral")
    default_voice_id = texttospeech.VoiceSelectionParams(
        language_code=selected_lang, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
        #audio_encoding=texttospeech.AudioEncoding.LINEAR16
        
        )

    #create an empty file
    # # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text="Start of the Podcast")
    voice = default_voice_id

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
        )

    with open(filename, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        #print('Audio content written to file "output.mp3"')
        
    # Split the text into lines and process each line.
    lines = text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line: #skip empty line
            continue

        if line.startswith("["):  # Skip timestamps if they exist.
            continue

        if line.startswith(v1Name):
        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
            speech_text = texttospeech.SynthesisInput(text=line[len(v1Name):].strip())

            response = client.synthesize_speech(
                    input=speech_text, 
                    voice=male_voice_id, 
                    audio_config=audio_config)  
            
            # The response's audio_content is binary.
            with open(filename, "ab") as out:
                # Write the response to the output file.
                out.write(response.audio_content)          
            
        elif line.startswith(v2Name):
            speech_text = texttospeech.SynthesisInput(text=line[len(v2Name):].strip())

            response = client.synthesize_speech(
                    input=speech_text, 
                    voice=female_voice_id, 
                    audio_config=audio_config)  
            
            # The response's audio_content is binary. append
            with open(filename, "ab") as out:
                # Write the response to the output file.
                out.write(response.audio_content)      

        else:  # Handle any unexpected lines (shouldn't happen in this script)
            print(f"Voice: Default voice used for line: {line}")
            
            response = client.synthesize_speech(
                    input=texttospeech.SynthesisInput(text=line), 
                    voice=default_voice_id, 
                    audio_config=audio_config)  
            
            # The response's audio_content is binary. append
            with open(filename, "ab") as out:
                # Write the response to the output file.
                out.write(response.audio_content)      
    print('Audio content written to file ' + filename)

    st.write('Audio content written to file ' + filename +'.')


############################
with tab3:
    if on2:

        ai_sys_instr='You are a podcast creator in language '+ selected_lang +'. Generate a podcast script with 2 hosts: '+ voice1Name + ' (a ' + voice1gender.lower() + ' voice) and '+ voice2Name + ' (a ' + voice2gender.lower() + ' voice). Return the results as plain text without any markdown.'
        st.text_area("Gemini System Instruction", value=ai_sys_instr, disabled=True, height=68)
        
        if len(article_txt) > 10:
            response = ai_client.models.generate_content(
                model=ai_model,
                contents=article_txt,
                config=types.GenerateContentConfig(
                    system_instruction=ai_sys_instr,
                    max_output_tokens = 8000,
                    top_k= 2,
                    top_p= 0.5,
                    temperature= 0.5,
                    response_mime_type= 'text/plain',
                    #stop_sequences= ['\n'],
                    seed=42,
                ),  
            )
            response_value= response.text
        else:
            response_value = ""

        # Assign a key to the widget so it's automatically in session state
        podcast_txt= st.text_area("Gemini generated podcast script...", value=response_value, disabled=False, height=68*5)
        st.write(f"Generated {len(podcast_txt)} characters for the podcast.")
        on3 = st.toggle("Finally: Generate Podcast Audio")

        #if st.button("Generate Podcast Audio", key="generate_button"):
        if on3:
            with st.spinner(text="In progress...", show_time=True):
                #pass the names and the gender
                audio1 = create_podcast(podcast_txt, "podcast_demo.mp3", voice1Name, voice2Name, voice1gender, voice2gender)
                st.spinner(text="File generated...")

                st.spinner(text="Creating audio player...")
                # show player
                audio_file = open("podcast_demo.mp3", "rb")
        
                audio_bytes = audio_file.read()
        
                st.audio(audio_bytes, format="audio/ogg",start_time=0)

                st.spinner(text="Done...")
