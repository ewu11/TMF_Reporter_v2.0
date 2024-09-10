import re
import streamlit as st
import os

def filter_messages(file_contents, base_names):
    # Define the timestamp pattern
    timestamp_pattern = re.compile(r'\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]|^\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [APM]{2}]')

    # Create a dynamic regex pattern for detecting variations of the base names
    name_patterns = [re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE) for name in base_names]

    filtered_lines = []
    skip_block = False
    current_message = []

    for line in file_contents.splitlines():
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
    
    return filtered_text

# Streamlit interface
st.title("Message Filtering App")

# Input area for base names
base_names_input = st.text_area("Enter base names (comma-separated)", "Hartina, Tina, Normah, Pom, Afizan, Pijan, Ariff, Dheffirdaus, Dhef, Hazrina, Rina, Nurul, Huda, Zazarida, Zaza, Eliasaph Wan, Wan, ] : , ] :")
base_names = [name.strip() for name in base_names_input.split(",")]

# File upload (support for up to 2 text files)
uploaded_files = st.file_uploader("Upload text files", type="txt", accept_multiple_files=True, max_files=2)

if uploaded_files and st.button('Cleanse file'):
    all_output = []
    
    for uploaded_file in uploaded_files:
        # Read file contents
        file_contents = uploaded_file.read().decode("utf-8")
        
        # Process the file and filter the messages
        filtered_text = filter_messages(file_contents, base_names)
        
        # Show the output in a text area
        all_output.append(f"Filtered content from {uploaded_file.name}:\n{filtered_text}")
    
    # Display the output for all files in a single text area
    st.text_area("Filtered Output", value="\n\n".join(all_output), height=400)
