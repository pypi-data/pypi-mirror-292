from setuptools import setup, find_packages

def parse_requirements(filename):
    """Read the requirements from a file."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='tts-stt-tools',
    version='1.0.1',
    description='A package for text-to-speech and speech-to-text tools',
    long_description=open('README.md').read(),  # Ensure you have a README.md file
    long_description_content_type='text/markdown',
    author='Sainag',
    author_email='sainag268@gmail.com',
    url='https://github.com/Sainag2473/tts-stt-tools',  # Replace with your project's URL
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    tests_require=['unittest'],
    test_suite='tests',
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'tts-stt-tools-speech=tts_stt_tools.tts:process_text_to_speech',
            'tts-stt-tools-text=tts_stt_tools.stt:process_speech_to_text',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
    ],
)
