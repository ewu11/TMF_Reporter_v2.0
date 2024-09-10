# import re
# import streamlit as st

# # Function to filter messages based on base names
# def filter_messages(file_contents, base_names):
#     timestamp_pattern = re.compile(r'\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]|^\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [APM]{2}]')
#     name_patterns = [re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE) for name in base_names]

#     filtered_lines = []
#     skip_block = False
#     current_message = []

#     for line in file_contents.splitlines():
#         if timestamp_pattern.match(line):
#             if current_message:
#                 filtered_lines.append(' '.join(current_message).strip().lower())
#                 current_message = []

#             if any(pattern.search(line) for pattern in name_patterns):
#                 skip_block = True
#             else:
#                 skip_block = False

#         if not skip_block:
#             current_message.append(line.strip().lower())

#     if not skip_block and current_message:
#         filtered_lines.append(' '.join(current_message).strip().lower())

#     return '\n\n'.join(filtered_lines)

# # Streamlit interface
# st.title("Message Filtering App")

# # Input area for base names
# base_names_input = st.text_area("Enter base names (comma-separated)", "Hartina, Tina, Normah, Pom, Afizan, Pijan, Ariff, Dheffirdaus, Dhef, Hazrina, Rina, Nurul, Huda, Zazarida, Zaza, Eliasaph Wan, Wan, ] : , ] :")
# base_names = [name.strip() for name in base_names_input.split(",")]

# # File upload (without max_files argument)
# uploaded_files = st.file_uploader("Upload text files", type="txt", accept_multiple_files=True)

# # Ensure only up to 2 files are processed
# if uploaded_files and len(uploaded_files) > 2:
#     st.error("You can only upload up to 2 files.")
# else:
#     if uploaded_files and st.button('Cleanse file'):
#         all_output = []
        
#         for uploaded_file in uploaded_files:
#             file_contents = uploaded_file.read().decode("utf-8")
#             filtered_text = filter_messages(file_contents, base_names)
#             all_output.append(f"===Filtered content from {uploaded_file.name}:===\n{filtered_text}")
        
#         combined_output = "\n".join(all_output)
        
#         # Insert CSS to disable the cursor change for disabled text_area
#         st.markdown(
#             """
#             <style>
#             .stTextArea textarea[disabled] {
#                 cursor: default;
#             }
#             </style>
#             """,
#             unsafe_allow_html=True
#         )

#         # Display the output in a disabled text area
#         st.text_area("Filtered Output", value=combined_output, height=400, disabled=True)

import re
import streamlit as st

# Initialize global result storage with various categories
global_result = {
    "Full Capping": [],
    "Order Missing/ Pending Processing": [],
    "Missing Manual Assign Button": [],
    "Other": []  # This will store both the ticket/ID and the message content
}

# Function to process the text file input
def process_messages_from_file(file_contents):
    global global_result
    
    messages = re.split(r'\n(?=\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} (?:am|pm)\])|\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]', file_contents)
    
    # Regular expressions for different patterns
    ticket_order_pattern = r'\b1-\d{9,11}\b|\bT-\d{9}\b|\bt-\d{10}\b|\b1-[a-z0-9]{7}\b|\binc\b'  # Ticket or order numbers
    id_pattern = r'\bQ\d{6}\b|\bq\d{6}\b|\bTM\d{5}\b|\btm\d{5}\b'  # ID numbers (e.g., Q107888)
    
    # Issue-specific patterns
    issue_patterns = {
        "Full Capping": r'\bfull cap[p]?ing\b',
        "Order Missing/ Pending Processing": r'\b(di|dlm|dalam) (oal|order(?: activity)?(?: list)?)\b',
        "Missing Manual Assign Button": r'\bma\b',  #ma btn xappear
    }

    # Result storage
    result = {
        "Full Capping": [],
        "Order Missing/ Pending Processing": [],
        "Missing Manual Assign Button": [],
        "Other": []  # Maybe due to invalid order/ticket number, no context, etc.
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

# Function to process all files
def process_uploaded_files(uploaded_files):
    global global_result
    global_result = {
        "Full Capping": [],
        "Order Missing/ Pending Processing": [],
        "Missing Manual Assign Button": [],
        "Other": []
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

# Streamlit app interface
st.title("Categorize File Contents")

# File upload for text files
uploaded_files = st.file_uploader("Upload text files", type="txt", accept_multiple_files=True)

# Button to trigger file categorization
if uploaded_files and st.button('Categorize file contents'):
    categorized_output = process_uploaded_files(uploaded_files)
    
    # Insert CSS to disable cursor change for disabled text_area
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
    st.text_area("Categorized Output", value=categorized_output, height=400, disabled=True)

