import streamlit as st
import re
import os
from pathlib import Path

# Define the main function to run in Streamlit
def filter_messages(input_folder_path, base_names, output_folder_path):
    # Check if the required files exist in the input folder
    required_files = ['ffRaw.txt', 'ttRaw.txt']
    missing_files = [file for file in required_files if not os.path.exists(os.path.join(input_folder_path, file))]

    if missing_files:
        st.error(f"The following required files are missing: {', '.join(missing_files)}.")
        return  # Exit the function if required files are missing
    
    timestamp_pattern = re.compile(r'\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]|^\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [APM]{2}]')

    # Ensure the output folder exists
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # Create a dynamic regex pattern for detecting variations of the base names
    name_patterns = [re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE) for name in base_names]

    # Get a list of all .txt files in the input folder
    input_files = [f for f in os.listdir(input_folder_path) if f.endswith('.txt')]

    progress_bar = st.progress(0)
    progress_step = 1 / len(input_files) if input_files else 0

    for i, file_name in enumerate(input_files):
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

        # Update progress bar
        progress_bar.progress((i + 1) * progress_step)

    return f"Processed {len(input_files)} files."

# Streamlit app starts here
st.title("Message Filter App")

# Get the path to the user's desktop
desktop_path = Path(os.path.expanduser("~/OneDrive - Telekom Malaysia Berhad/Desktop"))

# Input for folder paths
input_folder_name = st.text_input("Enter Input Folder Name", "ffTTReport")
output_folder_name = st.text_input("Enter Output Folder Name", "cleaned")

# Combine the desktop path with the folder name
input_folder_path = desktop_path / input_folder_name
output_folder_path = input_folder_path / output_folder_name

# Specify base names for filtering
base_names = ['Hartina', 'Tina', 'Normah', 'Pom',  'Afizan', 'Pijan', 'Ariff', 'Dheffirdaus', 'Dhef', 'Hazrina', 'Rina', 'Nurul', 'Huda', 'Zazarida', 'Zaza', 'Eliasaph Wan', 'Wan', '] : ', '] :']

# Button to trigger the processing
if st.button("Process Files"):
    if input_folder_path.exists():
        result = filter_messages(input_folder_path, base_names, output_folder_path)
        st.success(result)
    else:
        st.error(f"Input folder '{input_folder_name}' does not exist.")

# Display full paths
st.write(f"Input folder path: {input_folder_path}")
st.write(f"Output folder path: {output_folder_path}")
