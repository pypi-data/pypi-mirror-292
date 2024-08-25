import os
import shutil
import logging

# Configure logging to output debug information to a file and the console
log_file_path = os.path.join(os.path.dirname(__file__), 'copy_voices_debug.log')
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()  # Output logs to the console
    ]
)

def ensure_directory_exists(directory):
    """
    Ensure that the specified directory exists. Create the directory if it does not exist.

    Parameters:
    - directory (str): The path to the directory to check or create.
    """
    os.makedirs(directory, exist_ok=True)
    logging.debug(f"Ensured existence of directory: {directory}")

def copy_voices(source_dir, dest_dir):
    """
    Copy all files and subdirectories from the source directory to the destination directory.

    Parameters:
    - source_dir (str): The path to the source directory containing the voice models.
    - dest_dir (str): The path to the destination directory where voice models should be copied.
    """
    try:
        logging.debug(f"Starting copy from {source_dir} to {dest_dir}")

        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            dest_path = os.path.join(dest_dir, item)

            if os.path.isdir(source_path):
                # Copy directory and its contents
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                logging.debug(f"Copied directory: {source_path} to {dest_path}")
            else:
                # Copy individual file
                shutil.copy2(source_path, dest_path)
                logging.debug(f"Copied file: {source_path} to {dest_path}")

        logging.info(f"All files and directories copied successfully from {source_dir} to {dest_dir}")
    except Exception as e:
        logging.error(f"An error occurred while copying files: {e}")

def verify_directory_contents(directory):
    """
    List the contents of the specified directory to verify that files and subdirectories have been copied.

    Parameters:
    - directory (str): The path to the directory to list the contents of.
    """
    logging.debug(f"Verifying contents of {directory}")
    for root, dirs, files in os.walk(directory):
        level = root.replace(directory, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

def main():
    """
    Main function to ensure the destination directory exists, copy voice models from the source directory,
    and verify the contents of the destination directory.
    """
    source_directory = 'voices'  # Replace with the actual path to your source directory
    destination_directory = '/Users/sainagimmidisetty/.local/share/mycroft/mimic3/voices/'  # Replace with the actual path to your destination directory

    try:
        # Ensure destination directory exists
        ensure_directory_exists(destination_directory)

        # Copy voice models from source to destination
        copy_voices(source_directory, destination_directory)

        # Verify the contents of the destination directory
        verify_directory_contents(destination_directory)
    except Exception as e:
        logging.error(f"An error occurred during the process: {e}")
#
# if __name__ == "__main__":
#     main()
