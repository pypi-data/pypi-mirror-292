import os
import wave
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
import json
import logging
from .modelhelper import download_and_extract_model

# Configure logging
log_file_path = 'transcription_debug.log'  # Directly specify the log file path
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()  # Also output logs to the console
    ]
)

def convert_mp3_to_wav(mp3_path, wav_path):
    """
    Convert MP3 file to WAV format.

    Parameters:
    - mp3_path (str): Path to the MP3 file.
    - wav_path (str): Path to save the converted WAV file.
    """
    logging.debug(f"Converting MP3 to WAV: {mp3_path} -> {wav_path}")
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")
    logging.info(f"WAV file saved successfully as '{wav_path}'.")

def chunk_audio(wav_path, chunk_length_ms):
    """
    Chunk the WAV file into smaller segments.

    Parameters:
    - wav_path (str): Path to the WAV file.
    - chunk_length_ms (int): Length of each chunk in milliseconds.

    Returns:
    - list: List of AudioSegment chunks.
    """
    logging.debug(f"Chunking audio file: {wav_path}")
    audio = AudioSegment.from_wav(wav_path)
    chunks = [audio[i:i+chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    logging.info(f"Audio file chunked into {len(chunks)} segments.")
    return chunks

def transcribe_audio(chunk_path, model):
    """
    Transcribe audio from a WAV file.

    Parameters:
    - chunk_path (str): Path to the WAV file chunk.
    - model (Model): Vosk model for transcription.

    Returns:
    - str: Transcription result.
    """
    logging.debug(f"Transcribing audio chunk: {chunk_path}")
    with wave.open(chunk_path, 'rb') as wf:
        recognizer = KaldiRecognizer(model, wf.getframerate())
        final_result = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result_json = json.loads(recognizer.Result())
                final_result += result_json.get("text", "")
        final_result += json.loads(recognizer.FinalResult()).get("text", "")
    logging.info(f"Transcription complete for chunk: {chunk_path}")
    return final_result

def process_speech_to_text(mp3_path, output_directory, model_name, chunk_length_ms=1325000):
    """
    Process audio file: convert, chunk, and transcribe.

    Parameters:
    - mp3_path (str): Path to the MP3 file.
    - output_directory (str): Directory to save audio chunks.
    - model_name (str): Name of the Vosk model to use.
    - chunk_length_ms (int): Length of each chunk in milliseconds.

    Returns:
    - str: Full transcription of the audio file.
    """
    logging.info("Starting audio transcription process.")

    # Define model path
    model_dir = os.path.join(output_directory, model_name)

    # Check if model exists; if not, download and extract it
    if not os.path.exists(model_dir):
        logging.info(f"Model directory '{model_dir}' does not exist. Downloading and extracting model.")
        download_and_extract_model(model_name)
        print(model_dir)
        print(model_name)
    else:
        logging.info(f"Model directory '{model_dir}' already exists.")

    try:
        # Convert MP3 to WAV
        wav_path = os.path.join(output_directory, "audio.wav")
        convert_mp3_to_wav(mp3_path, wav_path)

        # Chunk the WAV file
        chunks = chunk_audio(wav_path, chunk_length_ms)

        print("model = Model(model_name)")
        # Load Vosk model
        model = Model(model_name)

        # Transcribe each chunk
        full_transcription = ""
        for i, chunk in enumerate(chunks):
            chunk_path = os.path.join(output_directory, f"chunk{i}.wav")
            chunk.export(chunk_path, format="wav")
            transcription_result = transcribe_audio(chunk_path, model)
            full_transcription += f"Chunk {i}:\n{transcription_result}\n\n"

        logging.info("Audio transcription process completed successfully.")
        return full_transcription

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

# def main():
#     """
#     Main function to run the audio transcription process with example paths.
#     """
#     mp3_path = "/Users/sainagimmidisetty/Desktop/BeyondProjectPhoenix/Module8_CaseStudies_Module9_ConclusionAndEndCredits.mp3"
#     output_directory = "/Users/sainagimmidisetty/Desktop/BeyondProjectPhoenix/chunks"
#     model_name = "vosk-model-en-us-0.42-gigaspeech"
#
#     if not os.path.exists(output_directory):
#         os.makedirs(output_directory)
#
#     transcription = process_audio_transcription(mp3_path, output_directory, model_name)
#     if transcription:
#         print(transcription)
#     else:
#         print("Transcription failed.")

# if __name__ == "__stt__":
    # main()
