# TTS-STT Tools

`tts-stt-tools` is a Python package designed to simplify text-to-speech (TTS) and speech-to-text (STT) conversions. This package provides an easy way to convert text into speech using various TTS systems and manage audio files efficiently.

## Features

- **Text-to-Speech (TTS)**: Convert text into speech with customizable voice models.
- **Speech-to-Text (STT)**: Convert speech into text using specified STT models.

## Installation

To install `tts-stt-tools`, follow these steps:

1. **Create and activate a virtual environment**:

    ```bash
    python3 -m venv testEnv1
    source testEnv1/bin/activate
    ```

2. **Install the package using `pip`**:

    ```bash
    python3 -m pip install --upgrade tts-stt-tools
    ```

## Usage

### Text-to-Speech

Convert text to speech with the following example:

1. **Import the package and initialize the TTS system**:

    ```python
    from tts_stt_tools import process_text_to_speech

    text = """
    Part three

    November 10–Present

    CHAPTER 14
    • Monday, November 10
    On Monday morning, Maxine is startled...
    """

    process_text_to_speech(text, voice_model='en_US/hifi-tts_low', filename='output.wav')
    ```

### Speech-to-Text

Convert speech to text using a specified model:

1. **Import the package and process the speech**:

    ```python
    from tts_stt_tools import process_speech_to_text

    mp3_path = "output.wav"
    output_directory = ""  # Specify the output directory if needed
    model_path = "vosk-model-small-en-us-0.15"  # Or use "vosk-model-en-us-0.42-gigaspeech"

    process_speech_to_text(mp3_path, output_directory, model_path)
    ```

### Optionally cleanup resources if needed:

```bash
deactivate
rm -r testEnv
rm -r testEnv1
rm -r *.log
rm -r *.wav
rm -r venv
rm -r ./Library/Jupyter/kernels/testenv
rm -r vosk-model-*
```
