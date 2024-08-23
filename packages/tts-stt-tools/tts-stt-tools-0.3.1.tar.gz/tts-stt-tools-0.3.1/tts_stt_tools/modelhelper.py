import os
import requests
import zipfile
import time
from tqdm import tqdm  # For progress bar

def download_model(url, download_path):
    """Download the model from the specified URL and save it to the specified path."""
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Check if the request was successful

    total_size = int(response.headers.get('content-length', 0))
    with open(download_path, 'wb') as f, tqdm(
        desc=download_path,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))
    print(f"Model downloaded successfully to {download_path}")

def extract_model(zip_path, extract_to):
    """Extract the downloaded zip file to the specified directory."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        total_files = len(zip_ref.namelist())
        with tqdm(total=total_files, desc='Extracting files') as bar:
            for file in zip_ref.namelist():
                zip_ref.extract(file, extract_to)
                bar.update(1)
    print(f"Model extracted to {extract_to}")

def download_and_extract_model(model_name):
    model_url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
    download_path = f"{model_name}.zip"
    extract_to = model_name

    if os.path.exists(extract_to):
        print(f"Model '{model_name}' already exists in '{extract_to}'. Skipping download.")
    else:
        start_time = time.time()
        download_model(model_url, download_path)
        extract_model(download_path, extract_to)
        os.remove(download_path)
        end_time = time.time()
        print("Temporary zip file removed.")
        print(f"Total time: {end_time - start_time:.2f} seconds")

# if __name__ == "__main__":
#     model_name = "vosk-model-en-us-0.42-gigaspeech"  # Replace with desired model
#     download_and_extract_model(model_name)
