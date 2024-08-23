
# TTS-STT Tools

`tts-stt-tools` is a Python package designed to simplify the process of text-to-speech (TTS) and speech-to-text (STT) conversions. With this package, you can easily convert text into speech using various TTS systems and manage audio files efficiently.

## Features

- **Text-to-Speech (TTS)**: Convert text into speech with customizable voice models.
- **Speech-to-Text (STT)**: Convert speech into text (if STT functionalities are included in future updates).

## Installation

To install `tts-stt-tools`, you can use `pip`. The package can be installed from PyPI using the following command:

```bash
python3 -m venv testEnv1
source testEnv1/bin/activate
python3 -m pip install --upgrade tts-stt-tools
```
### Example

1. **Import the package and initialize the TTS system:**

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

2. After completion deactivate and remove virtual environment if needed

```bash
deactivate
rm -r testEnv1
```


## Contributing

We welcome contributions to improve `tts-stt-tools`. If you want to contribute
