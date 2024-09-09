import streamlit as st
import re
from io import StringIO

# Initialize global result storage with various categories
global_result = {
    "Full Capping": [],
    "Order Missing/ Pending Processing": [],
    "Missing Manual Assign Button": [],
    "Other": []
}

# Function to process the text file input
def process_messages_from_string(content):
    global global_result
    messages = re.split(r'\n(?=\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} (?:am|pm)\])|\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]', content)

    # Regular expressions for different patterns
    ticket_order_pattern = r'\b1-\d{9,11}\b|\bT-\d{9}\b|\bt-\d{10}\b|\b1-[a-z0-9]{7}\b|\binc\b'
    id_pattern = r'\bQ\d{6}\b|\bq\d{6}\b|\bTM\d{5}\b|\btm\d{5}\b'
    
    # Issue-specific patterns
    issue_patterns = {
        "Full Capping": r'\bfull cap[p]?ing\b',
        "Order Missing/ Pending Processing": r'\b(di|dlm|dalam) (oal|order(?: activity)?(?: list)?)\b',
        "Missing Manual Assign Button": r'\bma\b|\bma btn xappear\b'
    }

    # Result storage
    result = {
        "Full Capping": [],
        "Order Missing/ Pending Processing": [],
        "Missing Manual Assign Button": [],
        "Other": []
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
                        result[issue].extend(i for i in ids if i not in added_ids)
                        added_ids.update(ids)
                else:
                    if tickets:
                        result[issue].extend(t for t in tickets if t not in added_tickets)
                        added_tickets.update(tickets)
                    if ids:
                        result[issue].extend(i for i in ids if i not in added_ids)
                        added_ids.update(ids)

                found_issue = True
                break

        if not found_issue:
            tickets = re.findall(ticket_order_pattern, message)
            ids = re.findall(id_pattern, message)
            if tickets or ids:
                if tickets:
                    result["Other"].extend([(t, message) for t in tickets if t not in added_tickets])
                    added_tickets.update(tickets)
                if ids:
                    result["Other"].extend([(i, message) for i in ids if i not in added_ids])
                    added_ids.update(ids)

    return result

# Streamlit app
st.title("Message Processing App")

uploaded_files = st.file_uploader("Choose text files", accept_multiple_files=True, type='txt')

if uploaded_files:
    # Read and process each uploaded file
    global_result.clear()
    for uploaded_file in uploaded_files:
        content = StringIO(uploaded_file.getvalue().decode('utf-8')).read()
        result = process_messages_from_string(content)

        # Update global result
        for key, value in result.items():
            if isinstance(value, list):
                global_result[key].extend(value)

    # Display results
    st.subheader("Processing Results")

    for issue, numbers in global_result.items():
        if numbers:
            st.write(f"**{issue}:**")
            if issue == "Other":
                for number, message in numbers:
                    st.write(f"{number} - Message: {message}")
            else:
                for number in numbers:
                    st.write(number)
