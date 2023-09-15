import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import requests
from bs4 import BeautifulSoup
import time

# Function to play audio prompts
def play_audio(text, lang='en'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("prompt.mp3")
    audio_file = open("prompt.mp3", "rb")
    st.audio(audio_file, format="audio/mp3")

# Function to get voice input from the user
def get_voice_input(prompt_text=None, lang='en'):
    recognizer = sr.Recognizer()
    while True:
        if prompt_text:
            play_audio(prompt_text, lang)
        time.sleep(2)  # Wait for 2 seconds after playing the audio prompt before listening
        with sr.Microphone() as source:
            st.text("Listening...")
            time.sleep(3)  # Pause for 3 seconds before starting to listen
            audio_data = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio_data, language=lang)
                st.text(f"You said: {text}")
                return text
            except:
                st.text("Sorry, I couldn't understand what you said.")

# Function to search the web and get records and links of the first few results
def search_web(query):
    query = query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        result_text = soup.find('div', class_='BNeawe').text
        links = [a['href'] for a in soup.find_all('a', href=True) if 'url?q=' in a['href']]
        st.write(f"**Search records:** {result_text}")
        st.write(f"**Source:** {' '.join([str(i+1)+'. '+l for i, l in enumerate(links[:1])])}")
        return result_text, links[:1]
    except:
        st.text("Sorry, no results found.")
        return None, []

# Streamlit app title
st.title("Jibran's Virtual Assistant")

# Starting point of the Streamlit app when the button is clicked
if st.button("Start Voice Input"):
    # Getting the preferred language from the user
    lang_choice = get_voice_input("In which language would you prefer to chat? English or Urdu?")
    
    # Mapping of language choices to language codes and corresponding prompts
    lang_map = {'english': 'en', 'urdu': 'ur'}
    lang_prompts = {
        'en': {
            'ask_name': "May I know your Name?",
            'assist': "! How may I assist you today?",
            'help_more': "Anything else that I can help you with, ",
            'further_help': "How can I help you further, ",
            'thank_you': "Thank you, "
        },
        'ur': {
            'ask_name': "آپ کا نام کیا ہے؟",
            'assist': "! آج میں آپ کی کس طرح کی مدد کر سکتا ہوں؟",
            'help_more': "کیا میں آپ کی مزید مدد کر سکتا ہوں, ",
            'further_help': "میں آپ کی مزید کس طرح کی مدد کر سکتا ہوں, ",
            'thank_you': "شکریہ, "
        }
    }
    
    # Setting the language based on the user's choice
    lang = lang_map.get(lang_choice.lower(), 'en')
    prompts = lang_prompts[lang]
    
    # Getting the user's name
    name = get_voice_input(prompts['ask_name'], lang)
    
    # Loop to handle the conversation flow
    while True:
        # Getting the user's query
        query = get_voice_input(f"{name}{prompts['assist']}", lang)
        
        # Searching the web for the answer to the query
        result_text, links = search_web(query)
        
        # Playing the search result as audio
        if result_text:
            play_audio(result_text, lang)
            time.sleep(len(result_text.split()) * 0.5)  # Waiting for the audio to finish playing based on the number of words in the result
        
        # Asking if the user needs further assistance
        time.sleep(2)  # Wait for 2 seconds before playing the next prompt
        more_help = get_voice_input(f"{prompts['help_more']}{name}? Please answer in Yes or No.", lang)
        
        # Handling the user's response for further assistance
        if more_help.lower() in ['yes', 'جی ہاں']:
            continue
        else:
            # Thanking the user and ending the conversation
            play_audio(f"{prompts['thank_you']}{name}!", lang)
            break
