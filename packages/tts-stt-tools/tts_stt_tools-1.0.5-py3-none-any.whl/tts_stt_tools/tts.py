"""
This module provides functions for text-to-speech conversion using the Mimic3 TTS system.

Functions:
- initialize_tts_system: Initializes the TTS system with a specified voice model and speaker.
- generate_audio: Generates audio data from text.
- save_audio: Saves audio data to a file.
- play_audio: Plays the audio file.
- process_text_to_speech: Orchestrates the text-to-speech process.
"""

from mimic3_tts import Mimic3TextToSpeechSystem, Mimic3Settings
import os
import platform
import logging

# Configure logging to output debug information to a file and the console
log_file_path = os.path.join(os.path.dirname(__file__), 'tts_debug.log')
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()  # Output logs to the console
    ]
)

def initialize_tts_system(voice_model='en_US/hifi-tts_low', speaker='92'):
    """
    Initialize the Mimic3 TTS system with the specified voice model and speaker.

    Parameters:
    - voice_model (str): The voice model to use for TTS. Default is 'en_US/hifi-tts_low'.
    - speaker (str): The speaker ID to use with the voice model. Default is '92'.

    Returns:
    - Mimic3TextToSpeechSystem: An instance of the TTS system configured with the given voice model and speaker.
    """
    logging.debug(f"Initializing TTS system with voice model: {voice_model} and speaker: {speaker}")

    # Set up TTS system settings with the specified voice model and speaker
    settings = Mimic3Settings(
        length_scale=1,
        noise_scale=0.33,
        noise_w=0.33,
        use_deterministic_compute=True
    )
    settings.voice = voice_model
    settings.speaker = speaker

    tts_system = Mimic3TextToSpeechSystem(settings=settings)
    logging.debug("TTS system initialized successfully.")

    return tts_system

def generate_audio(tts_system, text):
    """
    Generate audio data from the given text using the provided TTS system.

    Parameters:
    - tts_system (Mimic3TextToSpeechSystem): The TTS system instance.
    - text (str): The text to convert to audio.

    Returns:
    - bytes: The generated audio data in WAV format.
    """
    logging.debug("Generating audio from text.")

    # Convert text to audio using the TTS system
    audio_data = tts_system.text_to_wav(text)
    logging.debug("Audio generated successfully.")

    return audio_data

def save_audio(audio_data, filename="output.wav"):
    """
    Save the audio data to a specified file.

    Parameters:
    - audio_data (bytes): The audio data to be saved.
    - filename (str): The filename to save the audio data as. Default is 'output.wav'.
    """
    logging.debug(f"Saving audio to file: {filename}")

    try:
        # Write audio data to the specified file
        with open(filename, "wb") as f:
            f.write(audio_data)
        logging.info(f"Audio file saved successfully as '{filename}'.")
    except Exception as e:
        # Log any errors that occur while saving the audio file
        logging.error(f"Failed to save audio file: {e}")

def play_audio(filename="output.wav"):
    """
    Play the audio file using the appropriate command for the operating system.

    Parameters:
    - filename (str): The filename of the audio file to play. Default is 'output.wav'.
    """
    logging.debug(f"Playing audio file: {filename}")

    try:
        # Execute the appropriate command to play the audio file based on the OS
        if platform.system() == "Windows":
            os.system(f"start {filename}")
        elif platform.system() == "Darwin":  # macOS
            os.system(f"afplay {filename}")
        else:  # Linux
            os.system(f"aplay {filename}")
        logging.info(f"Audio file '{filename}' played successfully.")
    except Exception as e:
        # Log any errors that occur while playing the audio file
        logging.error(f"Failed to play audio file: {e}")

def process_text_to_speech(text, voice_model='en_US/hifi-tts_low', speaker='92', filename="output.wav"):
    """
    Process text-to-speech: convert text to speech, save the audio, and play it.

    Parameters:
    - text (str): The text to convert to speech.
    - voice_model (str): The voice model to use for TTS. Default is 'en_US/hifi-tts_low'.
    - speaker (str): The speaker ID to use with the voice model. Default is '92'.
    - filename (str): The filename to save the audio file as. Default is 'output.wav'.
    """
    logging.info("Starting text-to-speech process.")

    try:
        # Initialize the TTS system
        tts_system = initialize_tts_system(voice_model, speaker)

        # Generate audio from the given text
        audio_data = generate_audio(tts_system, text)

        # Save the audio to a file
        save_audio(audio_data, filename)

        # Play the audio file
        play_audio(filename)

        logging.info("Text-to-speech process completed successfully.")

    except Exception as e:
        # Log any errors that occur during the text-to-speech process
        logging.error(f"An error occurred: {e}")
