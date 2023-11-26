import os

def remove_files_in_directory(directory_path):
    try:
        # Iterate over all files in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            # Check if it is a file (not a directory)
            if os.path.isfile(file_path):
                # Remove the file
                os.remove(file_path)

    except Exception as e:
        print(f"An error occurred: {e}")