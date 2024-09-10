import re
import streamlit as st
from io import BytesIO

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

# Function to process all files for Process 1
def process_uploaded_files_filtering(uploaded_files, base_names):
    all_output = []

    for uploaded_file in uploaded_files:
        file_contents = uploaded_file.read().decode("utf-8")
        filtered_text = filter_messages(file_contents, base_names)
        all_output.append(f"===Filtered content from {uploaded_file.name}:===\n{filtered_text}")
    
    combined_output = "\n".join(all_output)
    return combined_output

# Streamlit interface for Process 1 (Message Filtering)
st.title("Message Filtering & Categorization App")

# Horizontal line between processes
st.markdown("---")

# Process 1: Input area for base names
base_names_input = st.text_area("Enter base names (comma-separated)", "Hartina, Tina, Normah, Pom, Afizan, Pijan, Ariff, Dheffirdaus, Dhef, Hazrina, Rina, Nurul, Huda, Zazarida, Zaza, Eliasaph Wan, Wan, ] : , ] :")
base_names = [name.strip() for name in base_names_input.split(",")]

# File upload for Process 1
uploaded_files_filter = st.file_uploader("Upload text files for filtering", type="txt", accept_multiple_files=True)

# Ensure only up to 2 files are processed for filtering
if uploaded_files_filter and len(uploaded_files_filter) > 2:
    st.error("You can only upload up to 2 files.")
else:
    if uploaded_files_filter and st.button('Cleanse file'):
        filtered_output = process_uploaded_files_filtering(uploaded_files_filter, base_names)
        
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
        st.text_area("Filtered Output", value=filtered_output, height=400, disabled=True)

        # Add a download button for the filtered text
        download_data = BytesIO(filtered_output.encode("utf-8"))
        st.download_button(
            label="Download Filtered Text",
            data=download_data,
            file_name="filtered_output.txt",
            mime="text/plain"
        )

# Horizontal line between processes
st.markdown("---")

# Process 2: Categorization logic remains the same as before
# Initialize global result storage with various categories
global_result = {
    "Full Capping": [],
    "Order Missing/ Pending Processing": [],
    "Missing Manual Assign Button": [],
    "Next Activity Not Appear": [],
    "Double @iptv": [],
    "Equipment New to Existing": [],
    "Design & Assign": [],
    "HSI No Password": [],
    "CPE New/ Existing/ Delete": [],
    "Update CPE Equipment Details": [],
    "Missing/ Update Network Details": [],
    "Update Contact Details": [],
    "Update Customer Email": [],
    "Bypass HSI": [],
    "Bypass Voice": [],
    "Bypass IPTV": [],
    "Bypass Extra Port": [],
    "Revert Order to TMF": [],
    "Release Assign To Me": [],
    "Propose Cancel to Propose Reappt/ Return": [],
    "Unsync Order": [],
    "Order Transfer SWIFT-TMF": [],
    "Duplicated Order Activity": [],
    "Reopen Jumpering": [],
    "TT RG6/ Combo Update": [],
    "TT CPE LOV": [],
    "TT Unable to Slot/ Error 400": [],
    "TT Missing/ Update Network Details": [],
    "TT V1P": [],
    "TT CPE Not Tally with Physical": [],
    "TT Link LR Appear TMF": [],
    "TT Blank Source Skill": [],
    "ID Locking/ Unlock/ 3rd Attempt": [],
    "TT Unsync": [],
    "TT Missing": [],
    "TT Update DiagnosisCode": [],
    "TT Granite Network Info Error": [],
    "TT HSBA Reappointment": [],
    "Resource Management Issue": [],
    "Other": []  # This will store both the ticket/ID and the message content
}

# Function to process messages from file (Process 2)
def process_messages_from_file(file_contents):
    global global_result
    messages = re.split(r'\n(?=\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} (?:am|pm)\])|\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]', file_contents)

    # Regular expressions for different patterns
    ticket_order_pattern = r'\b1-\d{9,11}\b|\bT-\d{9}\b|\bt-\d{10}\b|\b1-[a-z0-9]{7}\b|\binc\b'  # Ticket or order numbers
    id_pattern = r'\bQ\d{6}\b|\bq\d{6}\b|\bTM\d{5}\b|\btm\d{5}\b'  # ID numbers (e.g., Q107888)

    issue_patterns = {
        # Add issue patterns here as before...
    }

    # Track tickets and IDs already added
    added_tickets = set()
    added_ids = set()

    # Process each message block
    for message in messages:
        found_issue = False

        # Check for issues and collect tickets/IDs
        for issue, pattern in issue_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                tickets = re.findall(ticket_order_pattern, message)
                ids = re.findall(id_pattern, message)

                if issue == "Full Capping":
                    if ids:
                        global_result[issue].extend(i for i in ids if i not in added_ids)
                        added_ids.update(ids)
                else:
                    if tickets:
                        global_result[issue].extend(t for t in tickets if t not in added_tickets)
                        added_tickets.update(tickets)
                    if ids:
                        global_result[issue].extend(i for i in ids if i not in added_ids)
                        added_ids.update(ids)

                found_issue = True
                break

        # If no specific issue is found, categorize under "Other"
        if not found_issue:
            tickets = re.findall(ticket_order_pattern, message)
            ids = re.findall(id_pattern, message)
            if tickets or ids:
                if tickets:
                    global_result["Other"].extend([(t, message) for t in tickets if t not in added_tickets])
                    added_tickets.update(tickets)
                if ids:
                    global_result["Other"].extend([(i, message) for i in ids if i not in added_ids])
                    added_ids.update(ids)

# Function to process all files for categorization (Process 2)
def process_uploaded_files_categorization(uploaded_files):
    global global_result
    global_result = {
        # Reinitialize global result structure as before...
    }

    for uploaded_file in uploaded_files:
        file_contents = uploaded_file.read().decode("utf-8")
        process_messages_from_file(file_contents)
    
    # Output the accumulated result
    output = []
    for issue, numbers in global_result.items():
        if numbers:
            output.append(f"{issue}:")
            if issue == "Other":
                for number, message in numbers:
                    output.append(f"{number} - Message: {message}")
            else:
                for number in numbers:
                    output.append(number)
            output.append("")  # Blank line after each issue
    return "\n".join(output)

# File upload for Process 2
uploaded_files_categorize = st.file_uploader("Upload text files for categorization", type="txt", accept_multiple_files=True)

# Button to trigger file categorization
if uploaded_files_categorize and st.button('Categorize file contents'):
    categorized_output = process_uploaded_files_categorization(uploaded_files_categorize)
    
    # Display the output in a disabled text area
    st.text_area("Categorized Output", value=categorized_output, height=400, disabled=True)
