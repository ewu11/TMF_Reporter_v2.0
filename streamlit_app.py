import streamlit as st
import re

# Global result dictionary
global_result = {
    "Full Capping": [],
    "Order Missing/ Pending Processing": [],
    "Missing Manual Assign Button": [],
    "Other": []
}

# Define the main function to filter messages
def filter_messages(file_contents, base_names):
    timestamp_pattern = re.compile(r'\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]|^\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [APM]{2}]')
    name_patterns = [re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE) for name in base_names]
    filtered_lines = []
    skip_block = False
    current_message = []

    lines = file_contents.splitlines()
    for line in lines:
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

    filtered_text = '\n\n'.join(filtered_lines)
    return filtered_text

# Function to process the text file input
def process_messages_from_file(content):
    global global_result
    messages = re.split(r'\n(?=\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} (?:am|pm)\])|\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]', content)

    ticket_order_pattern = r'\b1-\d{9,11}\b|\bT-\d{9}\b|\bt-\d{10}\b|\b1-[a-z0-9]{7}\b|\binc\b'
    id_pattern = r'\bQ\d{6}\b|\bq\d{6}\b|\bTM\d{5}\b|\btm\d{5}\b'

    issue_patterns = {
        "Full Capping": r'\bfull cap[p]?ing\b',
        "Order Missing/ Pending Processing": r'\b(di|dlm|dalam) (oal|order(?: activity)?(?: list)?)\b',
        "Missing Manual Assign Button": r'\bma\b',
    }

    added_tickets = set()
    added_ids = set()

    for message in messages:
        found_issue = False
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

def process_uploaded_files(uploaded_files):
    global global_result
    global_result = {
        "Full Capping": [],
        "Order Missing/ Pending Processing": [],
        "Missing Manual Assign Button": [],
        "Other": []
    }

    for uploaded_file in uploaded_files:
        content = uploaded_file.read().decode("utf-8")
        st.write(f"Processing file: {uploaded_file.name}")  # Debug statement
        process_messages_from_file(content)

    st.write(f"Global Result: {global_result}")  # Debug statement
    return global_result

# Streamlit app starts here
st.title("Message Filter and Categorization App")

# Step 1: Upload the files
uploaded_files = st.file_uploader("Upload text files", type="txt", accept_multiple_files=True)

# Specify base names for filtering
base_names = ['Hartina', 'Tina', 'Normah', 'Pom', 'Afizan', 'Pijan', 'Ariff', 'Dheffirdaus', 'Dhef', 'Hazrina', 'Rina', 'Nurul', 'Huda', 'Zazarida', 'Zaza', 'Eliasaph Wan', 'Wan', '] : ', '] :']

# Step 2: Display process button after files are uploaded
if uploaded_files:
    if st.button("Filter and Categorize Files"):
        st.write("Processing files...")

        combined_output = ""
        for uploaded_file in uploaded_files:
            file_content = uploaded_file.read().decode("utf-8")
            filtered_text = filter_messages(file_content, base_names)
            combined_output += f"Filtered output for {uploaded_file.name}:\n{filtered_text}\n\n"

        result = process_uploaded_files(uploaded_files)

        categorized_output = "Categorized Results:\n"
        for issue, entries in result.items():
            if entries:
                categorized_output += f"\n{issue}:\n"
                if issue == "Other":
                    for number, message in entries:
                        categorized_output += f"{number} - Message: {message}\n"
                else:
                    for number in entries:
                        categorized_output += f"{number}\n"

        st.text_area("Filtered Content", combined_output, height=300)
        st.text_area("Categorized Results", categorized_output, height=300)
else:
    st.error("Please upload at least one text file.")
