import speech_recognition as sr
import pyttsx3
import wikipedia
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
import openai
import os
import math

# Initialize speech recognition and text-to-speech engines
r = sr.Recognizer()
engine = pyttsx3.init()

# Download NLTK data if needed
nltk.download('punkt')
nltk.download('wordnet')

# Set OpenAI API key from environment variable
openai.api_key = os.environ['OPENAI_API_KEY']

# Test OpenAI authentication
model_list = openai.Model.list()
print(model_list)

# Define a function to get the definition of a word
def get_definition(word):
    synset = wordnet.synsets(word)
    if synset:
        definition = synset[0].definition()
        return definition
    else:
        return None

# Define a function to generate text using OpenAI API
def generate_text(prompt):
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

# Define a function to respond to voice commands
def respond(audio):
    print(audio)
    engine.say(audio)
    engine.runAndWait()

# Main loop to listen for voice commands
while True:
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source, timeout=10, phrase_time_limit=5)

        try:
            command = r.recognize_google(audio).lower()
            print("You said: " + command)

            if "jarvis" in command:
                # Remove the wake word "jarvis" from the command
                command = command.replace("jarvis", "")

                # If the command is asking for a definition
                if "definition" in command:
                    # Get the word for which to find the definition
                    command = command.replace("definition", "")
                    word = word_tokenize(command)[0]
                    definition = get_definition(word)
                    if definition:
                        response = f"{word.capitalize()} is {definition}"
                    else:
                        response = f"I couldn't find a definition for {word}"
                    respond(response)

                # If the command is asking for information from Wikipedia
                elif "wikipedia" in command:
                    # Remove the word "wikipedia" from the command
                    command = command.replace("wikipedia", "")
                    # Search Wikipedia for the query
                    results = wikipedia.summary(command, sentences=2)
                    respond(results)

                # If the command is asking a math question
                elif "solve" in command:
                    # Remove the word "solve" from the command
                    command = command.replace("solve", "")
                    try:
                        # Evaluate the math expression
                        result = eval(command)
                        response = f"The answer is {result}"
                    except Exception:
                        response = "Sorry, I could not calculate that."
                    respond(response)

                # If the command is asking a general question
                else:
                    # Generate a response using OpenAI API
                    prompt = f"What is {command}?"
                    response = generate_text(prompt)
                    respond(response)

        except sr.UnknownValueError:
            respond("I'm sorry, I didn't understand that.")
        except sr.RequestError:
            respond("I'm sorry, I'm not able to process your request at the moment.")
