import re
import os
# import chardet
from pathlib import Path

# Function to detect file encoding using chardet and convert it to UTF-8
# def detect_and_convert_to_utf8(file_data):
#     raw_data = file_data.read()
    
#     # Detect the encoding using chardet
#     detected = chardet.detect(raw_data)
#     encoding = detected['encoding']
    
#     if encoding is None:
#         # st.warning("Could not detect the encoding. Assuming UTF-8.")
#         print("Could not detect the encoding. Assuming UTF-8.")
#         encoding = 'utf-8'
    
#     # Convert to UTF-8 using the detected encoding
#     try:
#         text_data = raw_data.decode(encoding)
#     except UnicodeDecodeError:
#         # st.error(f"Failed to decode the file using detected encoding: {encoding}.")
#         print("Failed to decode the file using detected encoding: {encoding}.")
#         return None

#     return text_data

def filter_messages(input_folder_path, base_names, output_folder_path):
    # Check if the required files exist in the input folder
    required_files = ['ffRaw.txt', 'ttRaw.txt']
    missing_files = [file for file in required_files if not os.path.exists(os.path.join(input_folder_path, file))]

    if missing_files:
        print(f"Error: The following required files are missing: {', '.join(missing_files)}.")
        print("Operation cancelled.")
        return  # Exit the function if required files are missing
    
    timestamp_pattern = re.compile(r'\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]|^\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [APM]{2}]')

    # Ensure the output folder exists
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # Create a dynamic regex pattern for detecting variations of the base names
    name_patterns = [re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE) for name in base_names]

    # Get a list of all .txt files in the input folder
    input_files = [f for f in os.listdir(input_folder_path) if f.endswith('.txt')]

    for file_name in input_files:
        # Detect and convert to UTF-8
        # file_content = detect_and_convert_to_utf8(file_data)
        # if file_content is None:
        #     continue  # Skip file if conversion fails
        
        file_path = os.path.join(input_folder_path, file_name)
        output_file_path = os.path.join(output_folder_path, file_name)

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        filtered_lines = []
        skip_block = False
        current_message = []

        for line in lines:
            # Check if the line starts with a timestamp, indicating a new message
            if timestamp_pattern.match(line):
                if current_message:
                    # If we have accumulated message lines, join them and add to the output
                    filtered_lines.append(' '.join(current_message).strip().lower())
                    current_message = []

                # Check if the line contains any of the base names or their variations
                if any(pattern.search(line) for pattern in name_patterns):
                    skip_block = True
                else:
                    skip_block = False

            # If not skipping, add the line to the current message
            if not skip_block:
                current_message.append(line.strip().lower())  # Convert to lowercase

        # Append the last message if it wasn't skipped
        if not skip_block and current_message:
            filtered_lines.append(' '.join(current_message).strip().lower())

        # Join the filtered lines back into a single string, ensuring each message is separated by '\n\n'
        filtered_text = '\n\n'.join(filtered_lines)

        # Save the filtered result to the output file
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(filtered_text)

    return f"Processed {len(input_files)} files."

# Get the path to the user's desktop
desktop_path = Path(os.path.expanduser("~/OneDrive - Telekom Malaysia Berhad/Desktop"))

# Specify your folder name
input_folder_name = "ffTTReport"
output_folder_name = "cleaned"

# Combine the desktop path with the folder name
input_folder_path = desktop_path / input_folder_name
output_folder_path = input_folder_path / output_folder_name

# Print the full folder path
print(f"Full path to the folder: {input_folder_path}")

# Ensure the folder exists, create if it doesn't
input_folder_path.mkdir(parents=True, exist_ok=True)
print(f"Folder '{input_folder_name}' is ready at: {input_folder_path}")

# Specify the base names to remove (core parts of the names)
base_names = ['Hartina', 'Tina', 'Normah', 'Pom',  'Afizan', 'Pijan', 'Ariff', 'Dheffirdaus', 'Dhef', 'Hazrina', 'Rina', 'Nurul', 'Huda', 'Zazarida', 'Zaza', 'Eliasaph Wan', 'Wan', '] : ', '] :']
# base_names = ['Hartina', 'Tina', 'Normah', 'Pom',  'Afizan', 'Pijan', 'Ariff', 'Dheffirdaus', 'Dhef', 'Hazrina', 'Rina', 'Nurul', 'Huda', 'Zazarida', 'Zaza', 'Eliasaph Wan', 'Wan']

# Get the result of processing files
result = filter_messages(input_folder_path, base_names, output_folder_path)

# Print the result
if result:
    print(result)
