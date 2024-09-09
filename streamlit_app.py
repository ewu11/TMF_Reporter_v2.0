import streamlit as st
import re

# Function to filter messages based on base names
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

# Initialize a variable to hold filtered results
filtered_results = {}

# Step 2: Process files when the button is clicked
if uploaded_files:
    if st.button("Process Files"):
        st.write("Processing files...")

        # Process each file
        for uploaded_file in uploaded_files:
            # Read file content
            file_content = uploaded_file.read().decode("utf-8")

            # Apply message filtering
            filtered_text = filter_messages(file_content, base_names)

            # Store the result in the dictionary
            filtered_results[uploaded_file.name] = filtered_text

        # Display the result in a text area for each file
        for file_name, filtered_text in filtered_results.items():
            st.subheader(f"Filtered output for {file_name}")
            st.text_area(f"Filtered content from {file_name}", filtered_text, height=300)

