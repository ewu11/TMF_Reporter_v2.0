import re
import streamlit as st

# Function to filter messages based on base names
def filter_messages(file_contents, base_names):
    timestamp_pattern = re.compile(r'\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]|^\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [APM]{2}]')
    name_patterns = [re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE) for name in base_names]

    filtered_lines = []
    skip_block = False
    current_message = []

    for line in file_contents.splitlines():
        if timestamp_pattern.match(line):
            if current_message:
                filtered_lines.append(' '.join(current_message).strip().lower())
                current_message = []

            if any(pattern.search(line) for pattern in name_patterns):
                skip_block = True
            else:
                skip_block = False

        if not skip_block:
            current_message.append(line.strip().lower())

    if not skip_block and current_message:
        filtered_lines.append(' '.join(current_message).strip().lower())

    return '\n\n'.join(filtered_lines)

# Streamlit interface
st.title("Message Filtering App")

# Input area for base names
base_names_input = st.text_area("Enter base names (comma-separated)", "Hartina, Tina, Normah, Pom, Afizan, Pijan, Ariff, Dheffirdaus, Dhef, Hazrina, Rina, Nurul, Huda, Zazarida, Zaza, Eliasaph Wan, Wan, ] : , ] :")
base_names = [name.strip() for name in base_names_input.split(",")]

# File upload (without max_files argument)
uploaded_files = st.file_uploader("Upload text files", type="txt", accept_multiple_files=True)

# Ensure only up to 2 files are processed
if uploaded_files and len(uploaded_files) > 2:
    st.error("You can only upload up to 2 files.")
else:
    if uploaded_files and st.button('Cleanse file'):
        all_output = []
        
        for uploaded_file in uploaded_files:
            file_contents = uploaded_file.read().decode("utf-8")
            filtered_text = filter_messages(file_contents, base_names)
            all_output.append(f"===Filtered content from {uploaded_file.name}:===\n{filtered_text}")
        
        combined_output = "\n".join(all_output)
        
        # Insert CSS to disable the cursor change for disabled text_area
        st.markdown(
            """
            <style>
            .stTextArea textarea[disabled] {
                cursor: default;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Display the output in a disabled text area
        st.text_area("Filtered Output", value=combined_output, height=400, disabled=True)
