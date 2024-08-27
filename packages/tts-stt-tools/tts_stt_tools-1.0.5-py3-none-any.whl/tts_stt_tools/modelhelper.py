import os
import requests
import zipfile
import time
import logging
from tqdm import tqdm  # For progress bar

# Configure logging to output messages to the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_model(url, download_path):
    """Download the model from the specified URL and save it to the specified path.

    Args:
        url (str): The URL to download the model from.
        download_path (str): The path to save the downloaded model.
    """
    logging.info(f"Starting download from {url} to {download_path}")

    try:
        # Perform HTTP GET request to download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check if the request was successful

        # Get the total size of the file from the response headers
        total_size = int(response.headers.get('content-length', 0))

        # Open file to write the downloaded content and set up progress bar
        with open(download_path, 'wb') as f, tqdm(
            desc=download_path,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            # Write chunks of the file to the local file and update progress bar
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))

        logging.info(f"Model downloaded successfully to {download_path}")
    except requests.RequestException as e:
        # Log an error if the download fails
        logging.error(f"Error downloading model: {e}")
        raise

def extract_model(zip_path, extract_to):
    """Extract the downloaded zip file to the specified directory.

    Args:
        zip_path (str): The path to the zip file to be extracted.
        extract_to (str): The directory to extract the zip file into.
    """
    logging.info(f"Starting extraction from {zip_path} to {extract_to}")

    try:
        # Open the zip file for extraction
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Count the number of files to extract for progress tracking
            total_files = len(zip_ref.namelist())
            # Set up progress bar for extraction
            with tqdm(total=total_files, desc='Extracting files') as bar:
                # Extract each file from the zip archive
                for file in zip_ref.namelist():
                    zip_ref.extract(file, extract_to)
                    bar.update(1)

        logging.info(f"Model extracted to {extract_to}")
    except zipfile.BadZipFile as e:
        # Log an error if extraction fails
        logging.error(f"Error extracting zip file: {e}")
        raise

def download_and_extract_model(model_name):
    """Download and extract the model specified by model_name.

    Args:
        model_name (str): The name of the model to be downloaded and extracted.
    """
    # Construct the URL for the model download
    model_url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
    download_path = f"{model_name}.zip"
    extract_to = ""  # Specify the directory to extract to

    # Check if the model already exists to avoid redundant downloads
    if os.path.exists(extract_to):
        logging.info(f"Model '{model_name}' already exists in '{extract_to}'. Skipping download.")
    else:
        # Record the start time for download and extraction
        start_time = time.time()
        try:
            # Download and extract the model
            download_model(model_url, download_path)
            extract_model(download_path, extract_to)
        finally:
            # Ensure the temporary zip file is removed after extraction
            if os.path.exists(download_path):
                os.remove(download_path)
                logging.info("Temporary zip file removed.")

        # Record the end time and log the total duration
        end_time = time.time()
        logging.info(f"Total time: {end_time - start_time:.2f} seconds")
