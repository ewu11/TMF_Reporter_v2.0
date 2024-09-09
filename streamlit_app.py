import streamlit as st
import re
import os
from pathlib import Path

# Define the main function to run in Streamlit
def filter_messages(file_contents, base_names):
    timestamp_pattern = re.compile(r'\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]|^\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [APM]{2}]')

    # Create a dynamic regex pattern for detecting variations of the base names
    name_patterns = [re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE) for name in base_names]

    filtered_lines = []
    skip_block = False
    current_message = []

    lines = file_contents.splitlines()

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

    return filtered_text

# Streamlit app starts here
st.title("Message Filter App")

# Step 1: Upload the files
uploaded_files = st.file_uploader("Upload text files", type="txt", accept_multiple_files=True)

# Specify base names for filtering
base_names = ['Hartina', 'Tina', 'Normah', 'Pom',  'Afizan', 'Pijan', 'Ariff', 'Dheffirdaus', 'Dhef', 'Hazrina', 'Rina', 'Nurul', 'Huda', 'Zazarida', 'Zaza', 'Eliasaph Wan', 'Wan', '] : ', '] :']

# Step 2: Process files when the button is clicked
if st.button("Process Files"):
    if uploaded_files:
        st.write("Processing files...")

        # Process each file
        for uploaded_file in uploaded_files:
            # Read file content
            file_content = uploaded_file.read().decode("utf-8")

            # Apply message filtering
            filtered_text = filter_messages(file_content, base_names)

            # Display the result
            st.subheader(f"Filtered output for {uploaded_file.name}")
            st.text_area(f"Filtered content from {uploaded_file.name}", filtered_text, height=300)
    else:
        st.error("Please upload at least one text file.")

# Display an arrow image to guide users to the next step
st.write("Proceed to the next step below:")
st.image("https://banner2.cleanpng.com/20180408/rpq/kisspng-application-for-employment-employment-website-care-down-arrow-5acac5ad9e6b47.1219531015232383176489.jpg", use_column_width=True)  # Display an arrow image at the end
