import streamlit as st
import re

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

# Function to process the text file input
def process_messages_from_file(content):
    global global_result

    # Split content into individual messages based on the pattern of new blocks
    messages = re.split(r'\n(?=\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} (?:am|pm)\])|\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]', content)

    # Regular expressions for different patterns
    ticket_order_pattern = r'\b1-\d{9,11}\b|\bT-\d{9}\b|\bt-\d{10}\b|\b1-[a-z0-9]{7}\b|\binc\b'  # Ticket or order numbers
    id_pattern = r'\bQ\d{6}\b|\bq\d{6}\b|\bTM\d{5}\b|\btm\d{5}\b'  # ID numbers (e.g., Q107888)

    # Issue-specific patterns
    issue_patterns = {
        "Full Capping": r'\bfull cap[p]?ing\b',
        "Order Missing/ Pending Processing": r'\b(di|dlm|dalam) (oal|order(?: activity)?(?: list)?)\b',
        "Missing Manual Assign Button": r'\bma\b',  # ma btn xappear
    }

    # Result storage for this run
    result = {
        "Full Capping": [],
        "Order Missing/ Pending Processing": [],
        "Missing Manual Assign Button": [],
        "Other": []
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

                # For "Full Capping," capture only IDs
                if issue == "Full Capping":
                    if ids:
                        global_result[issue].extend(i for i in ids if i not in added_ids)
                        added_ids.update(ids)
                else:
                    # For other issues, capture both tickets and IDs
                    if tickets:
                        global_result[issue].extend(t for t in tickets if t not in added_tickets)
                        added_tickets.update(tickets)
                    if ids:
                        global_result[issue].extend(i for i in ids if i not in added_ids)
                        added_ids.update(ids)

                found_issue = True
                break  # Stop once a matching issue is found

        # If no specific issue is found, categorize under "Other" and store both the message and ticket/ID
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

# Function to process all text files uploaded
def process_uploaded_files(uploaded_files):
    global global_result
    global_result = {  # Reset global result each time files are processed
        "Full Capping": [],
        "Order Missing/ Pending Processing": [],
        "Missing Manual Assign Button": [],
        "Other": []
    }

    for uploaded_file in uploaded_files:
        content = uploaded_file.read().decode("utf-8")  # Decode file content
        process_messages_from_file(content)

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

        # Process each file for filtering and categorization
        for uploaded_file in uploaded_files:
            # Read file content
            file_content = uploaded_file.read().decode("utf-8")

            # Apply message filtering
            filtered_text = filter_messages(file_content, base_names)
            combined_output += f"Filtered output for {uploaded_file.name}:\n{filtered_text}\n\n"

        # Apply categorization logic
        result = process_uploaded_files(uploaded_files)

        # Format the categorized results
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

        # Display the filtered content
        st.text_area("Filtered Content", combined_output, height=300)

        # Display the categorized results in the text area
        st.text_area("Categorized Results", categorized_output, height=300)

else:
    st.error("Please upload at least one text file.")
