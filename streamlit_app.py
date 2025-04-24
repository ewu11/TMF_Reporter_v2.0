import re
import streamlit as st
from io import BytesIO

# Function to filter messages based on base names
def filter_messages(file_contents, base_names):
    # timestamp_pattern = re.compile(r'\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]|^\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [APM]{2}]')
    timestamp_pattern = re.compile(r'\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} (?:am|pm)\]|\[\d{1,2}:\d{2} (?:am|pm), \d{1,2}/\d{1,2}/\d{4}\]|\[\d{1,2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]|^\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [APM]{2}]')
    name_patterns = [
        re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE) if re.match(r'\w+', name)
        else re.compile(rf'{re.escape(name)}', re.IGNORECASE)  # No word boundary for non-word characters
        for name in base_names
    ]

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
        all_output.append(f"===Cleansed content from {uploaded_file.name}:===\n{filtered_text}")
    
    combined_output = "\n\n".join(all_output)
    return combined_output

# Streamlit interface for Process 1 (Message Filtering)
st.title("TMF Reporter v2.0")

# Horizontal line between processes
st.markdown("---")

st.header("1. Text Cleansing")

# Process 1: Input area for base names
base_names_input = st.text_area("Enter names (to be removed when cleansing text file)", "Hartina, Tina, Normah, Pom, Afizan, Pijan, Ariff, Arep, Arip, Dheffirdaus, Dhef, Dheff, Dheft, Hazrina, Rina, Nurul, Huda, Zazarida, Zaza, Eliasaph, Wan, ] : , ] :")
base_names = [name.strip() for name in base_names_input.split(",")]

# File upload for Process 1
uploaded_files_filter = st.file_uploader("Upload text file for cleansing (max 2)", type="txt", accept_multiple_files=True)

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
        st.text_area("Cleansed Output", value=filtered_output, height=400, disabled=True)

        # Add a download button for the filtered text
        download_data = BytesIO(filtered_output.encode("utf-8"))
        st.download_button(
            label="Download cleansed text",
            data=download_data,
            file_name="cleansed_output.txt",
            mime="text/plain"
        )

# Horizontal line between processes
st.markdown("---")

st.header("2. Text Categorization")

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
    "Update Customer IC": [],
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
    "Patch Combo Flag (AX30002_5G no stock)": [],
    "Slotted HSBA Order, Remained Returned": [],
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
    "TT Invalid Activity Type": [],
    "Resource Management Issue": [],
    "TT Duplicated Activity": [],
    "TT Duplicate CPE SN#": [],
    "TT Expired CPE Warranty": [],
    "Invalid TT Info": [],
    "TaaS AOS Not Updated": [],
    "Others (to manually add into report)": []  # This will store both the ticket/ID and the message content
}

# Function to process messages from file (Process 2)
def process_messages_from_file(file_contents):
    global global_result
    # messages = re.split(r'\n(?=\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} (?:am|pm)\])|\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]|\[\d{1,2}:\d{2} (?:am|pm), \d{2}/\d{2}/\d{4}\]', file_contents)
    # messages = re.split(r'\[\d{1,2}:\d{2} (?:am|pm), \d{2}/\d{2}/\d{4}\]|\n(?=\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} (?:am|pm)\])|\[\d{2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]', file_contents)
    messages = re.split(r'\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} (?:am|pm)\]|\[\d{1,2}:\d{2} (?:am|pm), \d{1,2}/\d{1,2}/\d{4}\]|\[\d{1,2}:\d{2}, \d{1,2}/\d{1,2}/\d{4}\]|^\[\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [APM]{2}]', file_contents)
    
    # Regular expressions for different patterns
    ticket_order_pattern = r'\b1-\d{9,13}\b|\bT-\d{9}\b|\bt-\d{10}\b|\b1-[a-z0-9]{7}\b|\binc\b|\b25\d{13,14}\b'  # Ticket or order numbers
    id_pattern = r'\bQ\d{6}\b|\bq\d{6}\b|\bTM\d{5}\b|\btm\d{5}\b'  # ID numbers (e.g., Q107888)

    issue_patterns = {
        "Full Capping": r'\bfull cap(p)?ing\b|\bbukan dlm id ui\b|\bcap(p)?ing full\b|\b(tidak|x) as(s)?ign pd ru\b|\bfull slot\b|\btidak boleh ass(i)?gn pada team\b|\bslot id( ni)? x( ?)lepas\b|\bn(a)?k slot id\b|\bfull dalam list\b|\bcapping penuh\b|\bid.*full t(a)?p(i)? d(a)?l(a)?m list tmf.*ada \d order\b|\bui.*(tak|x) n(a)?mp(a)?k (d)?(e)?kat dia\b|\bui kata (x|tak) n(a)?mp(a)?k o(r)?d(e)?r\b|\bbukan ui pnya\b|\bslot balik p(a)?d(a)? (team|ru|ra|ui)\b|\border return(ed)? s(e)?m(a)?l(a)?m.*m(a)?s(i)?h ada d(a)?l(a)?m tm( )?f(orce)?.*ru\b|\bui inf(o)?(r)?m (t(a)?k|x) n(a)?mp(a)?k order\b|\bini order m(e)?m(a)?(n)?g ru p(u)?(n)?ya\b|\b(belum ada|xada|teda|tiada) id mana(2)? ru\b|\b(tidak|tak|x) d(a)?p(a)?t( )?(nak)?assign.*(ru|team)\b|\bord(er)?.*tak( )?d(a)?p(a)?t.*assign p(a)?d(a)? (team|ru)\b|\bbukan order (ui|team)\b|\bid( dah)?( )?full.*d(a)?l(a)?m tm( )?f(orce)?.*hanya ada [1-9] order\b|\b(takleh|xboleh|xleh) slot id\b|\bin( )?hand ui.*assign( ke)? ui\b|\bmasih full/7 order\b|\bin hand.*yg nak assign\b|\bid.*ada \d order t(a)?p(i)? id.*full\b|\bfull.*t(a)?p(i)?.*tm( )?f(orce)? ada \d order\b|\bo(r)?der (d(i)?|p(a)?d(a)?)( id)? ui\b|\bid ni.*(x|tak|tidak)( )?l(e)?p(a)?s.*slot order( lain)?\b|\bd(a)?h full (x|tak)( )?l(e)?p(a)?s slot( order)?\b|\border# ada dlm inhand.*order# nak assign ke ui\b|\btmf saya detect baru \d order\b|\border.*perlu.*masuk.*t(a)?p(i)? (x|tak)( )?(boleh|leh)( masuk)?\b|\bini b(u)?k(a)?n.*ini p(e)?(r)?lu.*masuk(kan)?\b|\btmf.*detect \d order\b|\bfull cappinng\b|\bcapping.*(full|p(e)?n(u)?h)\b|\border dah assign(ed)?.*id.*t(a)?p(i)?.*(tak|x) n(a)?mp(a)?k\b|\bid (ui|installer) n(a)?mp(a)?k (full|p(e)?n(u)?h)\b|\bid.*tm( )?f(orce)?.*(full|penuh)\b|\b(n(a)?k)? slot order x( )?l(e)?p(a)?s.*d(a)?l(a)?m id.*\d{1,2} order\b|\b(ru|ui) (x|t(a)?k) n(a)?mp(a)?k o(r)?d(e)?r\b|\bslot.*(full|penuh).*id b(a)?r(u)? ada \d{1,2} o(r)?der\b|\b(tak|x)( )?b(o)?l(e)?h slot ke id.*order.*\d{1,2} d(a)?l(a)?m (id|mobile|tab(let)?)\b|\bid q\d{6} (full|p(e)?nu(h)?)\b|\bb(e)?r(a)?p(a)? o(r)?der d(a)?l(a)?m id (ui|ra)\b|\bid (full|p(e)?n(u)?h).*sedia ada\b|\bid (full|p(e)?n(u)?h).*d(a)?l(a)?m id( ui| ru)?\b|\bini.*m(a)?h(u)? slot(ting)? d(e)?g(a)?n (ui|ru)\b|\border slot d(a)?l(a)?m id.*\d o(r)?d(e)?(r)? s(a)?(h)?(a)?(j)?(a)?\b|\bslot.*team.*ada \d\b|\bsemak.*id.*inhand \d o(r)?d(e)?(r)?.*(full|p(e)?n(u)?h)\b|\bid (ui|ru).*(full|penuh).*tm( )?f(orce)? ada \d\b|\border in(\-| )?hand.*order.*n(a)?k assign\b',
        "Order Missing/ Pending Processing": r'\b(di|dlm|dalam) (oal|order(?: activity)?(?: list)?)\b|\btmf (?:tak (?:wujud|appear)|x ?appear)\b|\b(di dlm oal|di oal|oal missing|tmf tak wujud|oal record not found|oal not found|oal xfound|oal xappear|oal not appear|oal x appear)\b|\b(?:tiada |masukkan |appear )?(?:order )?(dlm|dalam|in) rol\b|\b(tiada (dalam|dlm)|xda(?: di)?)( scheduled page)\b|\bponr\b|\b(.)?ending processing\b|\bmissing( dalam)? oal\b|\b(x?|tak ) masuk( di)?( dlm| dalam)( bakul| basket)\b|\b(?:order\s)?(?:tak\s|tiada\s|xda\s)?(?:masuk\s)?(?:dalam\s)?(?:bakul|basket)\b|\b(tiada|xda|takda) di( dalam)?( page)? activity\b|\btask sync\b|\bpending processing\b|\b(tak|x|tiada)\s*(?:di|dekat|dkt|dalam|dlm)?\s*(scheduled|unscheduled)( page)?\b|\btiada (dlm|dalam) (activity|act|aktivity|actvty) list\b|\b(xtvt|act|activity|actvty) (tak|x) (wujud|wjd)\b|\bmasukkan semula.*rol\b|\bstat(u)?(s)? unshedule(d)?.*(ra|mir|cc)\b|\bstatus( pending)?( )?processing\b|\bo(r)?d(e)?r.*(x|tak)( )?masuk (tmf|tmforce)\b|\b(order )?jadi unschedule(d)?\b|\breschedule(d)?( semula)? ke tm( )?f(orce)?\b|\border x( )?appear( at| di| in)? oal\b|\border ni ada (di)?( )?mana\b|\border return.*status unschedul(e)?(d)?\b|\bb(u)?(t)?t(o)?n return (tiada|xda|xde|takda)\b|\border return(ed)? jadi uns(c)?hedule(d)?\b|\border pending pro(c)?es(s)?ing\b|\border.*hilang.*id ui\b|\border ra.*(tak|x) (m(a)?s(u)?k d(a)?l(a)?m (act(ivity)?)|aktiviti|xtvt) order list\b|\bupdate semula ke rol\b|\b(tiada|xda) d(a)?l(a)?m ro(l|c)\b|\bescalate( )?(ke|m(a)?s(u)?k|d(a)?l(a)?m)?( )?rol\b|\border return j(a)?d(i)? unschedul(e)?(d)?\b|\bb(e)?l(u)?m appear d(a)?l(a)?m act(ivity)? list\b|\border (tidak|x|tak) n(a)?m(p)?(a)?k d(a)?l(a)?m.*d\b|\brecord not found.*slot\b|\bbelum appear di act sch list\b|\br(e)?c(o)?(r)?d (x|tak|not)( )?f(o)?(u)?(n)?d\b|\border ni(e)? (x|tak|not)( )?(a(p)?(p)?(e)?(a)?r|m(u)?(n)?c(u)?l)\b|\border.*(act(ivity)?|aktiviti|xtvt|actvty) (x|no|t(a)?k)( )?appear\b|\bo(r)?d(e)?r m(a)?s(i)?h processing\b|\bnot in r(e)?t(u)?(r)?n list\b|\b(ra|..|...) t(a)?p(i)? m(a)?s(i)?(h)? s(a)?(n)?gk(u)?t\b|\border.*return t(a)?p(i)? xd(a|e) b(u)?t(t)?(o)?n return\b|\bui.*order (tiada|teda|takd(e|a)|xd(e|a)) d(a)?l(a)?m (id|tab(let)?)\b|\bui inform (tiada|teda|takd(e|a)|xd(e|a)) d(a)?l(a)?m (id|tab(let)?)\b|\border.*(di|(d)?(e)?kat) m(a)?n(a)?\b|\bsudah assign.*(ru|ui).*(tiada|teda|t(a)?kd(a|e)) d(a)?l(a)?m (mobile|tab(let)?)\b|\border unschedul(e)?(d)?.*d(a)?l(a)?m (activity|xtvt|act|actvty) (list|p(a)?g(e)?)\b|\border (x|t(a)?k)( )?appear d(a)?l(a)?m scheduled p(a)?g(e)?\b|\border(?!.*slot(ted)?).*un( |-)?scheduled\b|\b(tiada|xda|takda)( d(a)?l(a)?m|in)?(..l|oal|..)\b|\bo(r)?d(e)?r.*(x( )?d(a|e)|tiada) p(a)?d(a)? schedule(d)?\b|\bo(r)?d(e)?r r(e)?t(u)?(r)?n.*m(a)?n(a)?\b|\bo(.)?d(.)?r.*found.*a(.)?t(i)?v(i)?t(.)?( list)?\b|\bo(r)?d(e)?(r)? (tiada|xd(a|e)) d(a)?l(a)?m (ao|oa)l\b|\b(tiada|xd(a|e)) oal\b|\bo(r)?d(e)?r.*p(a)?d(a)? id s(i)?(a)?(p)?(a)?\b|\border( ni)?( )?missing\b|\bui inform order h(i)?l(a)?ng.*tm( )?f(orce)? mobile\b|\b(t(.)?k|x)( )?n(.)?mp(.)?k.*d(.)?l(.)?m.*(tab|tm( )?f(orce)?)\b|\border.*m(a)?s(u)?k.*oal\b|\bo(.)?de(.)?.*(r|a)ol\b|\bo(.)?der.*(xd(.)?|t(.)?da|tiada).*d(.)?l(.)?m.*(act(.)?(.)?(.)?(.)?(.)?.*list|oal)\b|\border.*worklist.*ro.\b|r\bo(.)?der (?!.*slot(ted)?)(x|t(.)?(.)?d(.)?k|teda|).*d(.)?l(.)?m.*(tab|tm(.)?f(orce)?|mobile)\b|\bo(.)?der.*m(.)?s(.)?k.*(id|mobile|app|tm(.)?f(orce)?)\b|\bo(.)?der.*(ra|reappt).*k(.)?l(.)?(.)?r.*(akt(.)?(.)?(.)?(.)?(.)?|act(.)?(.)?(.)?(.)?(.)?)\b|\bo(.)?der(x|tiada|t(.)?k)(.*ad(.)?)?.*d(.)?l(.)?m.*(..|...)\b|\bo(.)?der.*status.*slot.*(ui|ru)\b|\b(sangkut )?oal x(.)?n(.)?mp(.)?k\b|\bd(.)?.*assign.*(..).*t(.)?(.)?(.)?ma\b|\bo(.)?d(.)?(.)?.*di (.)?(.)?(.)?schedul(.)?(.)? p(.)?g(.)?\b|\bo(.)?d(.)?(.)? processing rollback\b|\bo(.)?der.*pending oal\b|\bo(.)?der (t(.)?dak|x|t(.)?k) k(.)?luar.*(.)?(.)?(.)?sc(.)?(.)?dule(.)? p(.)?g(.)?\b|\b(..).*o(.)?d(.)?r (t(.)?k|t(.)?d(.)?(.)?|x) appear d(.)?l(.)?m (id|tab|app)\b|\b(ui|ru).*(t(.)?k|x|t(.)?d(.)?k)(.)?k(.)?l(.)?(.)?(.)? d(.)?l(.)?m tm(.)?f(orce)?.*(su)?d(.)?h ass(.)?(.)?(.)?ed.*ke (ui|ru|id)\b|\bo(.)?d(.)?(.)? not record found\b',
        "Missing Manual Assign Button": r'\bma\b|\b([.*]anual|man[n]?ual) (assign|slot|assgn|assigned)\b|\btm( )?f(orce)? (takdak|tiada|xd(a|e)) m(anual)?(.)?( )?assign\b|\b(assgt|ma|assign) m(a)?s(i)?h( )?( )?x( )?appear\b|\border unschedul(ed)?.*bantuan.*trigger.*ke status in( )?progres(s)?\b|\b(tiada|teda|(x|t(a)?kd(a|e)))( )?( )?b(u)?(t)?t(o)?n manual( )?( )?assign\b|\b(manual )?as(s)?(i)?(g)?n (not|t(a)?k|x)( )?a(p)?(p)?(e)?(a)?r\b|\bm(a)?(n)?(u)?(a)?l as(s)?(i)?(g)?(n)?(me(n)?)?(t)? (t(.)?k|x)( )?(appear|m(u)?nc(u)?l)\b|\bb(.)?(.)?(.)?(.)?(.)?(.)? manual as(.)?i(.)?(.)?\b|\b(tiada|t(.)?kda(.)?|teda|xd(a|e)).*(ma|manual assi(.)?(.)?)\b|\btiada manual bu(.)?ton\b',
        "Next Activity Not Appear": r'\bnext (aktiviti|act|activity|xtvt) tak appear\b|\b(xda|tiada) (cc|mir|ra)\b|\b(mir|ra|cc) (tiada|not appear|xappear|x appear|tak|x|missing)\b|\b(mir|ra|cc).*(ip|inprogress|missing)\b|\bnext (?:(owner|activity|act|actv))\b|\breturn(?: order)(?: list)\b|\bnot found(?: to)? (ra|mir|cc)\b|\bmir/?ra (in|ip)\b|\bcc (belum|x) appear\b|\b(mir|ra) in progress\b|\b(act|activity|activities|aktiviti) (x|not)\b|\b(masuk|masukkan)( ke (dalam|dlm))? rol\b|\bmasukkan order ke rol\b|\b(nxt|next)? (actvty|act|activities|activity|aktiviti) (not appear|xappear|xfound|not found|missing)\b|\blist rol\b|\bmasih unschedu(led)?\b|\bnpua|no pending user activity|pending (activity|act|activities|actvty)\b|\b(order )?(tiada|takda|xda) owner\b|\baktifkan order utk ra\b|\b(cc|ma|manual assign)(.*keluar|tiada)\b|\bpending (cc|ma|mir)\b|\b(nova )?(aktiviti|act|actvty|activity) (tidak)? [x]?update[d]?\b|\bt[u|i]?ada bu[t]?ton (cc|mir|ra)\b|\bmissing owner\b|\b(tak|x) k(e)?luar cc\b|\bno pending user\b|\b(cc|mir|ra) m(a)?s(i)?h (tak|x) appear\b|\b(ra|mir|cc) status in( |-)?progres(s)?\b|\bmasuk(kan)?.*r(r)?ol\b|\bnext (xtvt|act|activity|actvty|aktiviti).*appear\b|\bbelum (r)?rol\b|\bcc (t(i)?d(a)?k|tak|x) muncul\b|\btiada (butang|b(u)?(t)?t(o)?n) cc\b|\border (tiada|xd(e|a)) d(a)?l(a)?m roc\b|\b(confirmation call|cc) (tak|x|tiada) appear(ed)?\b|\btiada.*done cc\b|\bmir(\/)?( )?ra m(a)?s(i)?h in( )?progres(s)?\b|\bmir(\/)?( )?ra.*(in progress|(i)?( )?(p)?)\b|\bbelum.*(cc|mir|mir/ra) appear\b|\bmir( )?(&)?( )?ra\b|\bmi(r)?(-)?ip\b|\bcc( )?(not|x|t(a)?k)( )?( )?appear\b|\bo(r)?der m(a)?s(i)?h (sangkut|sekat|stuck|missing)\b|\border return(ed)? t(a)?p(i)? (tak ada|xda|teda) owner\b|\bmir.*done.*cc.*appear\b|\bcc( )?( )?(not|x)( )?appear\b|(cc|mir|ra) ❌|\b(cc|..|...) done.*(x|tak|not)( )?(a(p)?(p)?(e)?(a)?r|m(u)?(n)?c(u)?l|(a)?d(a|e))\b|\bdone (cc|..|...).*t(a)?p(i)?.*(t(a)?k|x)( )?b(o)?l(e)?h ass(i)?(g)?n\b|\b(cc|..|...) still (not|x|tak)( )?appear\b|\b(mir|ra) (not|x|t(a)?k)( )?appear(e)?(d)?\b|\bno next(t)? own(e)?(r)?\b|\bo(r)?der un(\-)?schedul(e)?(d)?\b|\bo(r)?der.*m(a)?s(i)?h ((ti|x)(a)?da|teda) task\b|\b(..|...) (not|tak|x)( )?app(a)?(e)?r\b|\b(..|...) in( |\-)?progres(s)?\b|\bro(c|l) b(e)?l(u)?m m(a)?s(u)?k lis(t)? (cxm|...|..)\b|\b(t(a)?k|x)( )?(a)?da b(u)?(t)?(t)?(o)?n r(e)?t(u)?(r)?n\b|\b(next)?( )?t(a)?sk o(r)?d(e)?(r)?\b|\bcc (no(.)?|..|...|....|.....) appear\b|\bantuan (mir|ra)\b(?!.*\b(tt|v1p)\b)|\bmir.*ra.*a(p)?(p)?(e)?(a)?r\b|\b(mir|ra) (not|x)( )?done\b|\bo(r)?d(e)?r.*return(..)?.*owner.*(ra|reap(p)?(t)?)\b|\b(still|m(a)?s(i)?h).*progres(.)?.*done(kan)? cc\b|\bo(r)?d(e)?r return.*next owner\b|\b(tiada|t(.)?k|x)( )?(a)?(da)?.*b(.)?(.)?(.)?(.)?n r(.)?t(.)?(.)?n\b|\b(mir|ra|mir(.)?ra).*(t(.)?k|x|tiada|t(.)?da).*appear\b|\b(ra|reappt).*semula.*o(.)?d(.)?r\b|\b((x|t(.)?k)d(a|e)|tiada|teda).*n(.)?xt.*o(.)?ner\b|\bo(.)?(.)?(.)?(.)?.*(mir|ra).*appear.*(oal|(.)?(.)?(.)?schedule(.)?).*p(.)?(.)?(.)?\b|\b(..|...) m(.)?s(.)?h in(.)?pr(.)?gre(.)?(.)?.\b|\bcc.*(x|not|t(.)?k).*ap(.)?(.)?(.)?r\b|\border book app(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?\b|\bmohon bantun cc\b|\b(.)?(.)?da(.)? (ra|reappt).*m(.)?s(.)?(.)?.*r(.)?t(.)?(.)?n( status)\b|\btiada next o(.)?(.)?ner\b|\bb(.)?(.)?(.)?(.)?n(.)? r(.)?t(.)?(.)?n.*appear.*tm(.)?f(orce)?\b|\b(su)?d(.)?(.)? swap no.*upd(.)?(.)?(.)? (act(ivity)?|akt(iviti)?).*done\b',
        "Double @iptv": r'\b(?:double )?iptv(?:@iptv)?\b',
        "Equipment New to Existing": r'\b(?:new )?(ke|to|kepada) (existing|exstng|existhing)\b|\bexisting(kan| kan?)( onu|btu|sp|router|wifi|wi-fi|rg|modem)\b|\btukar ke (existing|esxting)\b|\bmohon jadikan existing\b|\bupdate(d)?.*existing\b|\bmohon tukar.*existing\b|\bmohon existing( )?(kan)?\b|\bexisting(kan)?.*order relocat(e)?(d)?\b|\b(order relocate)?.*tukar.*(jadi|ke) ex(i)?(s)?ting\b|\bbantuan order force done cancel\b|\bmohon.*j(a)?di ex(i)?(s)?ting\b|\bj(a)?d(i)?k(a)?n.*ex(i)?(s)?ting\b|\border relocate existing( )?k(a)?n (btu|sp|mesh|service point)\b|\badd existing (mesh|sp|service point|rg|router|wifi|wi-fi)\b|\border relocate.*trigger existing\b|\bnew equipment ke exisiting\b|\bd(a)?r(i)? new ke e(s)?(x)?(i)?(s)?(t)?(i)?(n)?g\b|\bnew (e)?(q)?(u)?(i)?(p)?(m)?(e)?(n)?(t)? (k(e)?p(a)?(d)?(a)?|to) e(x)?(s)?(i)?(s)?(t)?(i)?(n)?g\b|\b(o(r)?d(e)?(r)? r(e)?l(o)?c(a)?t(e)?)? ex(i)?(s)?ting(kan)? (..|...|....|service point)\b|\bnew.*(to|k(e)?(p)?(a)?(d)?(a)?).*ex(s)?isting\b|\bex(i)?(s)?t(i)?(n)?(g)?k(a)?n (..|...|....|.....).*o(r)?d(e)?(r)?\b|\b(service point|..|...|....|.....|......).*ex..ti(n)?g\b|\bdari new ke(p)?(a)?(d)?(a)? ex(.)?(.)?(.)?(.)?(.)?ng\b|\bexis(.)?t(.)?ng(.)?(k(.)?n)? (..|...|....).*o(.)?d(.)?(.)? cuma migrate number\b',
        "Design & Assign": r'\b(d&a|dna|design|d&n (&|and) assign)\b|\bd&n\b|\bd&s ip\b|\bd( )?(&|n)( )?a ip\b|\bd( )?(&|n)?(a)?( )?(ip|in( |-)?progress)\b',
        "HSI No Password": r'\b(xda|tiada) (pw|password) (hsi|ppoe)\b|\b(xda|tiada) (hsi|ppoe) (pw|password)\b|\bnak (password|pw|pass|pword) h(s)?(i)?\b|\bp(a)?(s)?(s)?(w)?(o)?(r)?d ppoe\b|\breset ppoe\b|\bo(.)?d(.)?(.)?.*xd(.)?( ada)?(.)?(pw|pass|pwss) (.)?poe\b',
        "CPE New/ Existing/ Delete": r'\btukar existing\b|\b(extng|exstng|existing) (ke|to) new\b|\b(uonu|rg|btu|sp|wifi|router) (ke|kepada|to) new\b|^(?!.*\bwarranty\b)\b(update|updte|updt)\b(?!.*\bctt\b).*?( new)\b|\bexisting (to|ke|kpda|kepada) new\b|^(?!.*\b((.)?tt|activity|aktiviti|xtxt|actvty)\b)\b(m(o)?h(o)?n (del|delete).*(relocate)?\b|\bt(u)?k(a)?rkan existing.*new\b)|\b(upd(a)?t(e)?|add).*new.*order modify\b|\b(granite)?(service point|sp|btu).*subsequent\b|\badd new( ata)?\b|\bupdate(d)?.*(pd|kpd|kpada|kepada|pada).*new\b|\bcpe y(an)?g new hanya (mesh|rg|modem)?.*done.*exist(ing)?.*tukar\b|\btmf ad(a|e).*no del.*nova.*del\b|\border new install.*existing tukar new\b|\bb(a)?ntu tukar.*k(e)?p(a)?d(a)? combo\b|\badd (service point|sp|btu).*order modify\b|\badd (service point|sp|mesh) ke new\b|\border existing.*(eqp|equipment) (x|tak)( )?s(a)?m(a)?\b|\bbantuan.*replace cpe baru\b|\bminta b(a)?ntu del(ete)?( )?( )?existing\b|\bbantu del(ete)? (equipment|eqp|eqmnt)\b|\bdelete combo mesh\b|\badd.*d(a)?l(a)?m eq(u)?(i)?(p)?m(e)?n(t)?\b|\bbantu tukar(kan)? rg5 k(e|r) rg6.*order (ni|new install)\b|\border modify minta add (equipment|eqmnt|eqp)\b|\bmohon t(u)?k(a)?r (..|...|....) ke new\b|\border relocate.*mohon add (service point|..|....)\b|\border relocate.*t(u)?k(a)?r.*k(e)?p(a)?d(a)? new\b|\bbantu untuk add (service point|..|....) dekat (equipment|eqmnt|eqm(n)?t)\b|\border.*t(u)?k(a)?r(kan)?.*new (equipment|eqmnt|eqp)\b|\bmohon bantuan (u)?add (service point|..|....|...).*order modify\b|\border.*modify.*m(o)?h(o)?n (b(a)?(n)?t(u)?(a)?n)?.*(service point|..|...|....) new\b|\bubah (equipment|eqp|eq(p)?mnt) ke new\b|\b(equipment|eqmnt|eqp).*j(a)?d(i)?(kan)? del(ete)?\b|\bt(u)?k(a)?r (service point) ke new\b|\bb(a)?ntu del(ete)?.*d(a)?l(a)?m eq(u)?(i)?pm(e)?n(t)?\b|\btukar( )?(kan)?.*ke new\b|\bjadi( )?(kan)? (service point|..|...|....) (k(e)?p(a)?d(a)?|ke) new\b|\badd( )?(kan)?.*d(a)?l(a)?m sys(t)?(e)?(m)?\b|\bmohon (add|t(a)?mb(a)?h) (service point|..|...|....)\b|\bj(a)?d(i)?k(a)?n (service point|..|...|....) new\b|\badd (service point|..|...|....).*o(r)?der\b|\b(add|t(a)?mb(a)?h) (..|...|....|service point).*v(d)?(s)?(l)? (ke|to) f(f)?(t)?(t)?(h)?\b|\badd (service point|..|...|....).*new e(q)?(u)?(i)?(p)?(m)?(e)?(n)?(t)?\b|\b(..|...|....|.....).*new e(q)?(u)?(i)?(p)?(m)?(e)?(n)?(t)?\b|\bo(r)?d(e)?(r)? modify.*(uonu|combo)\b|\btukar(kan)? (service point|sp)?.*ke(p)?(a)?(d)?(a)?.*(new|delete|existing).*(uonu|combo|sp|service point)\b|\bforce done( )?(cancel)?.*combo.*(x|tak)( )?match.*mesh\b|\bt(u)?k(a)?r(kan)? (..|...|....|.....) ke(p)?(a)?(d)?(a)? new\b|\bj(a)?d(i)?(k(a)?n)?.*(..|...|....|.....) ke(p)?(a)?(d)?(a)? new\b|\bj(a)?d(i)?(k(a)?n)? (new|delete|ex..ting) rg.\b|\bo(r)?d(e)?r.*(modify|new).*t(a)?p(i)?.*ex..ting\b|\bcpe.*ada.*new.*m(.)?h(.)?n.*delete\b|^(?!.*\bctt\b)\btukar.*?(..|...|....|.....|......).*(k(.)?p(.)?d(.)?|to).*(new|delete|ex(.){0,5}g)\b|\bo(.)?de(.)?.*tukar(k(.)?n)? n(e)?w.*dari.*ke((.)?(.)?(.)?(.)?)?( )?(combo|rg6)\b|\b(del(ete)?|add|t(.)?mb(.)?h).*new.*(o(.)?der.*)?.*modify\b|\bt(.)?k(.)?r.*tag((.)?ing)?.*cpe.*(rg(.)?|combo)\b|\bdelete (..|...|....|.....).*apply.*s(.)?(.)?(.)?j(.)?\b|\bt(.)?k(.)?(.)?.*new (..|...|....|combo).*o(.)?der relo(.)?(.)?(.)?(.)?\b|\bdel(.)?(.)?(.)?.*(..|...|....|.....).*o(.)?der (modi(.)?(.)?|relo(.)?(.)?(.)?(.)?)\b|\badak(.)?n b(.)?r(.)?(.)?g.*proceed p(.)?s(.)?(.)?g.*(fd|force(.)?done) c(.)?nc(.)?l\b|\bo(.)?der.*update.*combo.*request.*baru\b|\btuka(.)? eq.*ke.*new\b|\bdel(.)?(.)?(.)?.*(rg|mesh|sp|btu|modem).*(t(.)?k|t(.)?d(.)?k|x)(.)?b(.)?l(.)?h done\b|\b(semak|check) cpe (..|...|....).*nova.*\d{1}.*tm(.)?f(orce)?.*\d{1}\b|\bnew(.)?k(.)?n (eqmnt|e(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?) o(.)?der relo(.)?(.)?(.)?(.)?\b',
        "Update CPE Equipment Details": r"\btidak boleh(?: (?:replace|update|tukar))? (?:cpe|rg|router|wifi|mesh|btu|sp|service point)\b|\border modify\b(?=.*\b(sn lama\/existing|sn baru)\b)|\bmodify (fixed|fix) ip\b|\border relocate guna existing cpe\b|\b(btn|button).*(replace|rplce).*(existing)?\b|\border force done( equipment)?.*(tak|x)( )?sama.*(tmf|tmforce)\b|\border.*fd\b|\btukar equipment daripada vm kepada sbvm\b|\bui.*scan.*keluar err(or)?\b|\b(tidak|x|tak) d(a)?p(a)?t complete order.*m(a)?s(a)?l(a)?h cpe\b|\bcomplete order.*onu combo: (unc.*|rg6.*|comb.*)\b|\bequipment.*(tak|x)( )?s(a)?m(a)? d(e)?n(g)?(a)?n mesh\b|\border relocation.*err(or)?.*done(kan)?\b|\border force done.*er(r)?(o)?(r)?\b|\bru sudah guna yang betul dan cpe ada dlm list ru\b|\bnak replace mesh tapi takde button save/update\b|\bcpe.*hanya ada (rg|mesh|btu|sp|onu)\b|\border relocate.*ru (tak boleh|xb(o)?l(e)?h) done order.*cpe existing\b|\borde(e)?(r)?.*t(a)?k bole(h)? complete.*t(a)?k bole(h)? (n(a)?k)? replace\b|\b(xleh|x( )?b(o)?l(e)?h) complete o(r)?der.*rg.*mesh\b|\btukar (..|....|.....|......) ke (..|....|.....|......).*tick r(e)?pl(a)?ce\b|\b(tak|x)( )?d(a)?p(a)?t complete order.*cpe (not|x|t(a)?k)( )?match\b|\border.*tukar (......|....|..|...).*replace equipment\b|\bo(r)?der relocate (x|tak)( )?b(o)?l(e)?h done.*cpe (x|tak)( )?b(o)?l(e)?h upd(a)?t(e)?\b|\btukar(kan)? ex(i)?st(i)?ng (rg(6)?|vm) k(e)?p(a)?d(a)? ex(i)?st(i)?ng.*combo\b|\bt(u)?k(a)?r(kan)? eq(u)?(i)?p(m)?(e)?n(t)?( )?( )?combo\b|\b(fd|force done).*err(or)? cpe no match\b|\b(tak|x)( )?b(o)?l(e)?h done(kan)? order\b|\b(t(a)?k|x)( )?b(o)?l(e)?h.*done.*o(r)?de(r)? relocate cpe.*existing\b|\b(t(i)?(d)?ak|)( )?d(a)?p(a)?t upd(a)?t(e)? cpe.*c(o)?mpl(e)?t(e)? o(r)?der\b|\bui (t(a)?k|x)( )?b(o)?l(e)?h n(a)?k t(u)?k(a)?r eq(u)?(i)?(p)?(m)?(e)?n(t)? d(a)?l(a)?m tm( )?f(orce)?\b|\bcpe ada d(a)?l(a)?m list t(a)?p(i)? k(e)?l(u)?(a)?r.*b(i)?l(a)?.*s(u)?b(m)?(i)?t\b|\breplace(ment)? cpe( u(n)?t(u)?k scan)?\b|\b(vm|..|...) ke (uonu)( )?(-)?( )?(combo)\b|\b(o)?(r)?d(e)?r vdsl t(a)?p(i)?.*combo\b|\badd (..|...|....).*tukar (rg6|combo)\b|\bo(r)?d(e)?(r)?.*(t(a)?k|x)( )?b(o)?l(e)?h r(e)?pl(a)?(c)?(e)? (..|...|....|service point)\b|\b(t(ia|e)da|xd(a|e)) b(u)?(t)?(t)?(o)?n u(n)?t(u)?k upd(a)?(t)?(e)? e(q)?(u)?(i)?(p)?(m)?(e)?(n)?(t)?\b|\border modify.*j(a)?d(i)?(k(a)?n)? combo( )?(box)?\b|\br(e)?pl(a)?ce ex(.)?(.)?t(i)?ng router.*(rg6|combo)\b|\bt(u)?k(a)?r cpe.*ke(p)?(a)?(d)?(a)?.*combo\b|\b(order modify)?.*t(.)?k(.)?r(k(.)?n)? (service point|..|...|....).*((.)?onu|..|...|....).*(order modify)\b|\berr(.)?(.)?.*upd(.)?(.)?(.)?.*s(.)?n.*2.5g(.)?(.)?(.)?.*slims\b|\bby( )?pas(.)? o(.)?de(.)?.*(fd|force done).*kerja(2)?.*(p(.)?(.)?(.)?(.)?(.)?(.)?l|f(.)?(.)?(.)?(.)?(.)?(.)?)\b|\bdone.*t(.)?(.)?(.)?(.)? k(.)?(.)?(.)?(.)?(.)?(.)?.*(p(.)?(.)?(.)?(.)?(.)?(.)?l|f(.)?(.)?(.)?(.)?(.)?(.)?)\b|\bby(.)?pas(.)? e(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?.*(fd|force done)\b|\bdone.*o(.)?der.*update(.)?.*(cpe)?.*tm( )?f(orce)?\b|\brelocate.*tukar(kan)?.*(..|...|....|.....)\.*ke.*(..|...|....|.....)\b|\bdone(kan)?.*o(.)?der.*(fd|force done)\b|\brenew contract.*cpe.*lama\b|\bn(.)?k upd(.)?(.)?(.)? cpe (t(.)?k|x) l(.)?p(.)?s\b|\bo(.)?der.*n(.)?k.*done.*err(.)?(.)?.*eq(.)?(.)?p(.)?(.)?(.)?(.)?( (x|t(.)?k)(.)?s(.)?m(.)?)?\b|\bn(.)?k.*done.*t(.)?p(.)?.*e(.)?(.)?(.)?(.)?\b|\bbantu.*(ui|ru).*(tak|x)(.)?b(.)?l(.)?(.)?.*done.*o(.)?der\b|\bo(.)?der (force(.)?done|fd).*b(.)?l(.)?h(.)?(n(.)?k)?(.)?done\b|\bo(.)?der relo(cate)?.*(t(.)?k|x)(.)?b(.)?l(.)?h complete o(.)?d(.)?r\b|\beq(.)?(.)?p(.)?(.)?(.)?(.)?.*(t(.)?k|x|t(.)?d(.)?k) s(.)?m(.)? nak done o(.)?der (t(.)?k|x|t(.)?d(.)?k) b(.)?l(.)?h\b|\bo(.)?d(.)?r relo(cate)?.*pair.*(x|t(.)?k|t(.)?d(.)?k) s(.)?m(.)?\b|\bo(.)?d(.)?r modi(fy)?.*n(.)?k d(.)?n(.)? (x|t(.)?k|t(.)?d(.)?k)(.)?l(.)?p(.)?s.*s(.)?(.)?gk(.)?t.*eq(.)?(.)?p(.)?(.)?(.)?(.)?\b|\bo(.)?d(.)?r modify.*t(.)?k(.)?r (btu|sp|modem).*eq(.)?(.)?p(.)?(.)?(.)?(.)?.*(x|t(.)?k|t(.)?d(.)?k) b(.)?l(.)?h d(.)?n(.)?\b",
        "Missing/ Update Network Details": r"\b(fail to )?(slot )?(?!.*\b\d{1,4}[-/:]\d{1,4}[-/:]?\d{0,4}\b)(?!.*\b\d{1,2}[:]\d{2}\b)(appointment|appmnt|apmt|appmt)\b\b|\btukar(kan)? (building|cab|cabinet|fdp|fp|fdc|dc)\b|\bxleh n(a)?k slot\b|\bgranite n(e)?twork info\b|\bft order ke hari ini\b|\bbooking c(a)?l(a|e)?nder (tak|x) keluar date available\b|\bgranite fail(ed)?\b|\brefresh granite info\b|\bslot not available\b|\bfailed to ra\b|\bexchange (berlainan|lain) d(a)?l(a)?m tm( )?f(orce)?.*nova b(e)?t(u)?l\b|\bfail(ed)?.*refresh n(e)?tw(o)?(r)?k\b|\bslot tiada\b|\bo(r)?d(e)?r.*(d(e)?t(a)?(i)?l|info).*granite\b|\bn(.)?k t(.)?k(.)?r (.)?d(.)?\b|\bm(.)?h(.)?n (info|d(.)?t(.)?(.)?l) gr(.)?n(.)?(.)?(.)?\b|\b(info|d(.)?t(.)?(.)?l) gr(.)?n(.)?(.)?(.)? (t(.)?k|x|t(.)?d(.)?k) k(.)?l(.)?(.)?r.*tm(.)?f(orce)?\b|\bgr(.)?n(.)?(.)?(.)?.*k(.)?l(.)?(.)?(.)?.*(info|data|d(.)?t(.)?(.)?l|m(.)?kl(.)?m(.)?t)\b",
        "Update Contact Details": r"\b(updt|updte|update) (contact|ctc|hp|phone|mobile)( num| number)?\b|\b(tukar|tukarkan|tkr) (contact|ctc|phone)( number| #| num)?\b|\bctc num\b|\bremove nombor( pic)?\b|\bal(a)?m(a)?t order\b|\bupdate no (ctc|contact)\b|\b(change|ubah|upd(a)?t(e)?) c(o)?(n)?t(a)?c(t)? number\b|\bu(p)?(d)?(a)?t(e)? c(o)?(n)?(t)?(a|e)?(c)?t n((u)?(m)?(b)?(e)?(r)?|o(m)?|u(m)?)\b|\bupd(a)?(t)?(e)? n(u|o)?mb(e|o)?r\b|\bupd(.)?(.)?(.)?.*(contact|ctc)\b|\btukar(k(a)?n)? (n(u|o)m(b(.)?r)?).*ke(p(.)?d(.)?)?\b|\b(upd(.)?(.)?(.)?|trig(.)?(.)?(.)?) nam(.)? cust(.)?(.)?(.)?(.)?\b|\bup(.)?(.)?(.)?(.)? c(.)?(.)?t(.)?c(.)? (n(.)?mb(.)?r|no)\b|\bamend cust((.)?m(.)?r) (c(.)?(.)?t(.)?c(.)?|phone|hp) (#|no|number)\b",
        "Update Customer IC": r"\bic no.*invalid\b|\bicbrn invalid\b|\binvalid ic\/br\b|\bicbr invalid\b",
        "Update Customer Email": r"\bemail.*salah\b|\bb(.)?t(.)?(.)?(k(.)?n) email o(.)?der\b",
        "Bypass HSI": r"\b(bypass|done|skip|donekan) (aktivity|act|activity|activities|actvty)?hsi\b|\bhsi.*bypas(s)?\b|\bby( )?pas(s)? h(si|is)\b|\bqos\b|\bdone( )?kan (hsi|his)\b|\bsession up verify fail\b|\bmohon by( )?pas(s)?( act(ivity)?)? hsi\b|\bbypas(s)?( testing)? (hsi|his)\b|\bby( )?pas(s)?.*(hsi|his)\b|\bo(r)?d(e)?r (force done|fd).*by( )?pas(s)? verification\b|\border t(a)?k d(o)?n(e)? b(o)?l(e)?h by( )?pas(s)?\b|\border modify.*(force done|fd) tanpa kerja( kerja)? (f(i)?z(i)?k(a)?l|ph(y)?s(i)?c(a)?l)\b|\bfailed verify service testing hsi\b|\bverify h(si|is).*reboot\b|\bgated.*su(.)?(.)?e(.)?(.)?\b|\b(fizikal|physical).*hsi.*internet\b|\bh(si|is).*fail(.)?(.)?\b",
        "Bypass Voice": r"\b(by pass|bypass).*voice\b|\bvobb.*bypass\b|\b(voice|vobb).*bypas(s)?\b|\bmohon by( )?pas(s)?( act(ivity)?)? voice\b",
        "Bypass IPTV": r"\b(by pass|bypass).*iptv\b|\biptv.*bypas(s)?\b|\bbypas(s).*upb\b|\bmohon by( )?pas(s)?( act(ivity)?)? ip( )?(tv)?\b",
        "Bypass Extra Port": r"\b(by pass|bypass) (extraport|extrapot|extra port|extra pot)\b|\bby( )?pas(s)? xp\b|\bbantuan bypass kan extraport\b|\bmohon by( )?pas(s)?( act(ivity)?)? (extra( )?port)\b|\bby( )?pas(s)? ext(r)?a( )?port\b|\bby( )?pas(s)? gated extra( )?po(r)?t\b|\bby( )?pas(.)? (e)?xtra( |-)?port\b|\bby(.)?p(.)?s(.)? extra(.)?por(.)?.*fail(.)?(.)?\b|\bby(.)?pa(.)?(.)? fdp cleansing\b",
        "Revert Order to TMF": r"\brevert (order|order2).*ke(.*|tmf)\b|\bremove mdf\b|\br(e)?v(e)?(r)?t o(r)?d(e)?r id\b",
        "Release Assign To Me": r"\brelease (assign(?: to me)?|assgn)\b|\brelease(kan)? order\b|\brelease(kan)?( order)?( dari)? id\b|\bfail to slot\b|\brelease(kan)?( )?( )?dr id\b|\breleasekan( )?( )?order\b|\bfail(ed)? to rescheduled\b|\brelease from me\b|\brelease kan order\b|\brelease(k(a)?n)? order\b|\brelease(kan)? assign to me\b|\brelese(kan)?( order)?\b|\bmohon bantu r(e)?lease\b|\bmohon release(kan)?\b|\bfail to ra\b|\bbantuan release(kan)?.*1-(8|9)\d{10,11}.*q[0-9]{5,6}\b|\bfail(ed)?( )?( )?to (ra|reapp(t)?)\b|\bslot fail.*(ra|reapp(t)?)\b|\bslot fail(ed)?\b|\bfail(ed)? to slot(t)?\b|\border.*fail(ed)? ra(a)?\b|\brelease(kan)?.*assign to me\b|\border fail(ed)?.*un(\-)?sch(a|e)dule(d)? page\b|\bun(\-)?sch(a|e)dule(d)? o(r)?d(e)?r fail(ed)?.*upd(a)?t(e)?\b|\b(tak|x)( )?b(o)?l(e)?h( )?(n(a)?k)?( )?slot\b|\ber(.)?(.)?r.*slot a(p)?(p)?(o)?(i)?(n)?(t)?(m)?(e)?(n)?(t)?\b|\b(.|..|...)( )?d(a)?p(a)?t.*slot t(a)?r(i)?kh\b|\bo(r)?d(e)?r.*fail.*slot.*app(.)?(.)?(.)?(.)?(.)?(.)?(.)?t\b|\bfail slot\b|\bre(.)?(.)?(.)?(.)?(.)?.*(book app(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?|ra|reap(.)?(.)?)\b|\bfail(.)?(.)?.*(to|u(.)?t(.)?k).*(slot|reap(.)?(.)?|rea(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?)\b|\b(t(.)?k|x) b(.)?l(.)?h (s(.)?l(.)?ct|pilih) (d(.)?t(.)?|t(.)?r(.)?(.)?(.)?(.)?) app(.)?(.)?t\b|\bo(.)?der.*b(.)?l(.)?(.)?.*(reappt|ra|slot)\b|\bra order.*keluar page\b|\bgagal book ap(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?t\b|\bcl(.)?(.)?r(k(.)?n)? assign to me\b|\b(r(.)?m(.)?v(.)?|del(ete)?) tag as(.)?(.)?g(.)? to me\b|\bt(.)?k b(.)?l(.)?h n(.)?k (ra|reappt)\b|\bn(.)?k (ra|reappt) o(.)?d(.)?(.)? t(.)?k b(.)?l(.)?h\b",
        "Propose Cancel to Propose Reappt/ Return": r"\brcl|propose cancel|propose reappt\b|\brtn cancel\b|\brrol\b|\border proposed cancel.*nak proceed pasang\b|\brevert semula dari propose(d)? cancel ke (r)?rol\b|\baktif(kan)? s(e)?m(u)?la order( silap)? return(ed)? cancel((l)?ed)?\b|\br(e)?t(u)?(r)?n cancel(led)?.*proceed ra\b|\border propose(d)? cancel(led)? n(a)?k (ra|reappt)\b|\bput back to rol\b|\brevert.*ke rol d(a)?r(i)? propos(e)?(d)? cancel(led)?\b|\bpropo(.)e cancel(led)?.*ra\b|\border.*propose(.)? cancel.*proceed semula\b|\bprop(.)?(.)?(.)?(.)? return\b|\bpropose(.)? cancel.*proceed ra\b",
        "Unsync Order": r"\bstatus not sync\b|\bunsync(h|ed)? order\b|\b(dalam|dlm) tmf( masih)?( status)? assign(ed)?\b|\bdone (tapi|tp) status( masih)? (ip|in progress|in-progress|inprogress)\b|\btmf.*schedule(d)?.*t(e)?(t)?(a)?p(i)?.*(nova)?complete(d)?.*(nova)?\b|\b(mohon )?tarik atau cancel (dari|dr) (tmf|tm( )?force)\b|\border.*status complete(d)?.*(x)( )?h(i)?l(a)?(n)?g d(a)?r(i)? tm( )?f(orce)?\b|\bt(e)?t(a)?p(i)? status m(a)?s(i)?h in( |-)?progress d(a)?l(a)?m( portal)? tm( )?f(orce)?\b|\bprocessing-complete\b|\bdone pending complete(d)?\b|\border( d(a)?h)? siap.*t(a)?p(i)?.*m(a)?s(i)?h processing\b|\bstatus.*(not|tak|x).*sync((h)?ed)? tm( )?f(orce)?.*nova\b|\b(activity|xtvt|aktivity).*nova done.*tm()?f(orce)?.*w(u)?j(u)?d\b|\btukar status k(e)?p(a)?d(a)? complet(ed)?\b|\border return(ed)? t(a)?p(i)? unschedule(d)?\b|\bcomplete(kan)? order.*p(e)?m(a)?s(a)?(n)?g(a)?n (siap|sudah|settle|beres)\b|\bd(a)?h done.*status.*(in( )?progress|ip).*d(a)?l(a)?m.*tm( )?f(orce)?\b|\border (x( )?sync(h)?(ed)?|unsynch(ed)?)\b|\border.*return(ed)?.*st(a)?t(u)?s unschedul(ed)?\b|\border.*st(a)?t(u)?s r(e)?t(u)?(r)?n.*o(r)?d(e)?r j(a)?d(i)? c(o)?mplete(d)?\b|\border.*return(ed)?.*tm( )?f(orce)?.*(ip|in( )?progres(s)?).*nova\b|\bbantu comp(.)eted.*o(r)?der.*sd\d{6,7}\b|\breturn j(a)?d(i)? un( |\-)?schedul(e)?(d)?\b|\bo(r)?d(e)?r m(a)?s(i)?h un( |\-)?schedule(d)?\b|\border st(a)?t(u)?s c(o)?mpl(e)?t(e)?.*(ui|ra) b(e)?l(u)?m c(o)?mpl(e)?t(e)?(kan)?\b|\bo(r)?d(e)?r st(a)?t(u)?s c(o)?mp(l)?(e)?t(e)?(d)? t(a)?p(i)?.*not started\b|\bj(a)?d(i)?(k(a)?n)? complete(d)?\b|\border return.*jadi unsche....(d)?\b|\bunschedule(d)?.*(ra|reappt)\b|\bunmatch(ing)? o(.)?d(.)?r status\b|\bcomplete(kan)?.*order(.)?.*partial complete(.)?\b|\bo(.)?d(.)?r.*complete(.)?.*masih.*(appear|m(.)?nc(.)?l)\b|\bprocessing complete(d)?\b|\bo(.)?de(.)?.*status.*complete(d)?.*(tiad(a|e)|x( )?d(a|e)|teda).*ui.*done\b|\breturn((.)?(.)?)?.*j(.)?d(.)?.*uns(.)?chedul(.)?(.)?\b|\bcomplete(.)?.*tm( )?f(orce)?.*(ip|in(.)?progres(.)?)\b|\bo(.)?der.*ret(.)?(.)?n.*m(.)?s(.)?h.*(di( d(.)?l(.)?m)?|(.)?(.)?k(.)?t).*tm(.)?f(orce)?\b|\b(su)?da(.)?.*p(.)?s(.)?ng.*t(.)?p(.)?.*(processing|p(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?g)\b|\bo(.)?der.*c(.)?mpl(.)?t(.)?.*in(.)?pr(.)?gre(.)?(.)?\b|\bsaf.*(onsite|tos|v2p).*(x|t(.)?k).*b(.)?l(.)?h\b|\bo(.)?der re(.)?(.)?(.)?n(.)?(.)? (t(.)?p(.)?|j(.)?d(.)?).*(un)?s(.)?(.)?(.)?dule(.)?\b|\border ta(.)?(.)? syn(.)?(.)?(.)?\b|\bo(.)?der.*status.*(ip|in(.)?prog(.)?(.)?(.)?(.)?).*(.)?(.)?t(.)?p(.)?.*id\b|\bo(.)?der.*done.*t(.)?p(.)?.*(ip|in(.)?progre(.)?(.)?)\b|\bo(.)?der.*r(.)?t(.)?(.)?n(ed)?.*t(.)?p(.)?.*slot(ted)?\b|\bstat(.)?(.)?.*unscheduled\b|\bdone (ra|reappt) t(.)?p(.)?.*return(.)?(.)?\b|\bo(.)?der(.)?(status)?(.)?submi((.)?ted)?\b|\bmohon (ra|reschedule|slot) o(.)?d(.)?r(.)?.*p(.)?d(.)?.*t(.)?l(.)?h (ra|reschedule|slot) p(.)?d(.)?.*(x|t(.)?k|t(.)?d(.)?k) b(.)?l(.)?h t(.)?k(.)?r (tarikh|d(.)?t(.)?) ke\b|\bins(tallation)? d(.)?n(.)?.*t(.)?p(.)? st(.)?t(.)?(.)? m(.)?s(.)?(.)? (ip|in(.)?pr(.)?gr(.)?s(.)?)\b|\bt(.)?l(.)?(.)?g clear o(.)?der.*tm(.)?f(orce)?.*complete(.)?\b|\bo(.)?d(.)?r (x|not) complete(.)?\b",
        "Order Transfer SWIFT-TMF": r"\bmohon transfer ke tmf\b|\btransfer order ni ke tm( )?f(orce)?\b",
        "Duplicated Order Activity": r"\bduplicate(d)? di( )?(portal|tm( )?f(orce)?)?\b",
        "Reopen Jumpering": r"\border dah slot.*x( )?n(a)?mp(a)?k d(a)?l(a)?m tm( )?f(orce)?\b",
        "Patch Combo Flag (AX30002_5G no stock)": r"\bby( )?pas(s)?( )?(flag)? combo\b|\bby( )?pas(s)? order.*modify (1|2)gb\b|\b(ru|ui) p(a)?s(a)?ng combo.*(tiada|xd(a|e) sto(c)?k).*(done submit form)?\b|\bo(r)?der (1|2)gb(ps)?( proceed)?( )?combo\b|\bm(i)?nta git(d)? d(a)?r(i)? combo (ax)?2.5g(hz)? ke(p)?(a)?(d)?(a)? combo ax300(.)? s(e)?b(a)?b (t(i)?d(a)?k ad(a|e)|tiada|x( )?d(a|e)) sto(c)?k\b|\bby( )?pas(s)?( flag)?.*order (1|2)gb(ps)? p(a)?k(a)?i combo biasa\b|\bt(u)?k(a)?r(kan)? cpe ke(p)?(a)?(d)?(a)? ax300(.)?\b|\bdah s(u)?bm(i)?t cust(omer)? p(a)?k(a)?i (1|2)gb(ps)?\b|\bby( )?pas(s)? cpe order new (1|2)gb(ps)?\b|\bby( )?pas(s)? cpe.*order (1|2)gb(ps)? guna combo\b|\bby( )?pas(s)?.*combo( box)? ax300(.)?\b|\bby( )?pas(.)?( )?k(a)?n cpe\b|\bby( )?pas(.)?(kan)?.*(1|2)gb(ps)?.*combo\b|\bby( )?pas(s)? o(r)?d(e)?r 2.5g.*combo biasa\b|\bby( )?pas(s)?( )?(k(a)?n)?.*( combo)?( )?2.5g\b|\bru.*combo( )?(box)? ax300(.)?.*ax3000 2.5g.*sto(c)?k\b|\bt(u)?k(a)?r( )?(kan)? cpe combo biasa.*o(r)?d(e)?r (1|2)gb(ps)?\b|\bbantu(an)? by( )?pas(.)?.*done s(u)?bm(i)?t\b|\bo(r)?d(e)?r (1|2)g(b)?(ps)? t(u)?k(a)?r( )?(k(a)?n)?.*combo 2.5g.*combo ax300(.)?\b|\bby( )?pas(s)?( )?(kan)? cpe o(r)?der.*done\b|\bby( )?pas(s)?(k(a)?n)?.*t(u)?k(a)?r.*(1|2)g(b)?(p)?(s)? ke ax300(.)?\b|\border (1|2)g(b)?(p)?(s)?.*by( )?pas(s)?.*ax300(.)?\b|\bt(u)?k(a)?r( )?(k(a)?n)?.*ax300(.)? 2.5(g)?.*ax300(.)?\b|\bt(u)?k(a)?r( )?(kan)?.*ax300(.)?.*sto(c)?k.*(1|2)g(b)?(p)?(s)?\b|\bby( )?pas(s)?.*o(r)?der (1|2)g(b)?(p)?(s)?\b|\bby( )?pas(s)?.*ax300(.)?\b|\bt(u)?k(a)?r(k(a)?n)?.*ax300(.)? (1|2)g(b)?(p)?(s)?.*ax300(.)?\b|\bo(r)?d(e)?r (1|2)g(b)?(p)?(s)?.*p(a)?k(a)?i combo\b|\bby( )?pas(.)?.*combo 2.5(g)?\b|\b(tiada|tak( )?ad(a|e)) sto(c)?k combo 2.5(g)?\b|\bby( )?pas(.)? cpe\b|\bby( )?pas(.)? o(r)?d(e)?r.*new install (1|2)g(b)?(p)?(s)?\b|\bo(r)?d(e)?r (1|2)g(b)?(p)?(s)?\b|\b(1|2)g(b)?(p)?(s)?.*t(u)?k(a)?r(k(a)?n)? e(q)?(u)?(i)?(p)?(m)?(e)?(n)?(t)?\b|\bt(u)?k(a)?r(k(a)?n)?.*ax300(.)?.*2.5(g)?\b|\bt(u)?k(a)?r(k(a)?n)? e(q)?(u)?(i)?(p)?(m)?(e)?(n)?(t)?.*ax300(.)?.*(1|2)g(b)?(p)?(s)?\b|\bun( )?gate.*ax300(.)?.*(1|2)g(b)?(p)?(s)?\b|\bby( )?pas(.)? (1|2)g(b)?(p)?(s)?\b|\b(1|2)g(b)?(p)?(s)? ke combo\b|\b2.5g(b)?(p)?(s)? ke ax( )?300(.)?\b|\bcombo.*((1|2)|1\/2)g(b)?(p)?(s)?.*o(r)?d(e)?r\b|\bby( )?pas(.)?.*sto(c)?(k)? combo\b|\b2.5(b)?(p)?(s)?.*combo.*ax300(.)?\b|\bby( )?pas(.)?.*(1|2)g(b)?(p)?(s)?\b|\b2\.5g.*combo(.)?.*biasa\b|\bt(u)?k(a)?r.*(d(o)?n(e)?|d(a)?h).*isi (form|b(o)?r(a)?ng)\b|\b(o(.)?d(.)?r)?.*combo ax300(.)?.*(o(.)?d(.)?r)?.*form.*isi\b|\b2( )?(g)?(b)?(p)?(s)? ke ax300(.)?\b|\bby(.)?pas(.)?(modify.*)?rg.*ax( )?300(.)?\b|\bt(u)?k(a)?r.*combo.*ax( )?300(.)?.*sto(.)?k\b|\bflag 2.5(.)?(.)?(.)?(.)?.*combo\b|\border.*done.*combo 2.5g\b|\bt(.)?k(.)?r.*2.5g(.)?(.)?(.)?\b|\bo(.)?d(.)?r (1|2)( )g(.)?(.)?(.)?.*proceed.*combo\b",
        "Slotted HSBA Order, Remained Returned": r"\bo(.)?der.*slot(ted)?.*portal.*tm(.)?f(orce)?.*return(ed)?\b|\bo(.)?der.*slot(ted)?.*portal.*tapi.*tm(.)?f(orce)? m(.)?s(.)?h status\b|\bbantu(.)?(.)?.*slot(kan)?.*(appt|appmnt|ap(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?).*asal\b|\ba(.)?(.)?ist to ch(.)?(.)?g(.)? to or(.)?g(.)?(.)?(.)?(.)? timing for below o(.)?der(.)?\b|\brequest to slot as original date\b|\bo(.)?der slotted t(.)?p(.)?.*return(.)?(.)?.*un(.)?(.)?(.)?(.)?dul(.)?(.)?\b|\bo(.)?der.*slot(ted)?.*m(.)?si(.)?(.)?.*array\b|\bmove (..) uns(.)?(.)?(.)?dule(.)?\b",
        "TT RG6/ Combo Update": r"\bnew (rg|router|wifi|mesh|btu|sp|service point)\b|\bs\/?n baru\b|\bold.*sn.*new\b.*\b(unc.*|mt.*|wfh.*|rg6.*|rgx.*|hp.*|com.*|uon.*)\b|\b(c)?tt.*(combo box|cbox|combo) sn: \b|\b(c)?tt.*(rg|rg6|combo|cbox|combo box)\b.*\b(unc|mt|wfh|rg6|rgx|hp|com|uon).*\b|^(?!.*\b((by( )?pas(s)?)|f(i)?z(i)?k(a)?l)\b)(.*\b(serial no|sn|serial)( baru| lama)\b.*\b(unc|mt|wfh|rg6|rgx|hp|com|uon).*)|\bold.*sn.*(new)( rg)?\b.*\b(unc|mt|wfh|rg6|rgx|hp|com|uon).*\b|\bold.*sn.*(new)(.*)?\b.*\b(unc|mt|wfh|rg6|rgx|hp|com|uon).*\b|\bsn rg baru( )?( )?:( )?(unc|mt|wfh|rg6|rgx|hp|com|uon).*\b|\btukar combo box.*(s(\/)?n|serial number)\b|\btukar.*combo.*(s(\/)?n|serial number)\b|\beqpmnt sama tapi keluar error\b|\b(x ?|tak ?)d(a)?p(a)?t (tukar|tkr).*(rg.*|com.*).*upgrade.*mb(p)?(s)?\b|\bcpe does not exist in hand\b|\b(tidak|x|tak) d(a)?p(a)?t t(u)?k(a)?r rg(5|6)\b|\bd(a)?p(a)?t err(or)?.*t(u)?k(a)?r cpe.*sn rg :( )?\b|\bmaklum pelanggan change equipment\b|\btiada detail.*equipment.*sn: \b|\b(replace)?( )?rg(4|5) (to|k(e)?p(a)?d(a)?) (rg6|combo)\b|\brg lama.*combo baru\b|\b(c)?tt no:  1-(1|8|9)\d{9,13}  lama :  baru : (unc[a-z0-9]{14,16}|rg[a-z0-9]{14,16})\b|\b(c)?tt.*1-(1|8|9)\d{10,13}.*baru.*lama( )?:( )?\b|\b1-(1|8|9)\d{9,13}.*rg[a-z0-9]{10,18}.*unc[a-z0-9]{10,18}\b|\b(serial number|sn(#)?) does no(t)? exist in your cpe list\b|\b1-(1|8|9)\d{10,13}.*(cpe|sn(#)?) lama.*(cpe|sn(#)?) baru\b|\btukar flag (c)?tt\b|\brevert d(a)?r(i)?(p(a)?d(a)?)? combo ke(p(a)?d(a)?)? router\b|\b(p(a)?(k)?(e)?j|p(a)?(c)?(k)?(a)?(g)?(e)?).*(..|...) lama.*combo\b|\bt(u)?k(a)?r rg\/onu( ke)? combo( ctt)?\b|\b(c)?tt.*(x|tak)( )?b(o)?l(e)?h.*swap (..|...|....)\b|\b1-\d{9,13}.*rg6.*unc.*\b|\b1-\d{9,13}\s*unc\S*\s*rg(x|6)\S*\b|\b(c)?tt.*n(a)?k t(u)?k(a)?r (..|...|....|.....|......)\b|\bflag.*combo.*new s(\/)?n.*old s(\/)?n\b|\b(c)?tt\s*:\s*[^\s]*\s*new\s*:\s*[^\s]*\s*old\s*:\s*[^\s]*\b|\bcombo.*new( )?(...|..).*old( )?(...|..)\b|\b(c)?tt.*new cpe( )?(:)?( )?.*(unc|rg6).*old cpe\b|\b(c)?tt.*sn( ..| ...)?.*lama.*sn( ..| ...)?.*baru.*(unc|rg6).*[\d][^\s]\b|\btukar(kan)? flag.*(rg6|combo).*old.*new\b|\b(c(.)?(.)?(.)?(.)?(.)?|t(.)?(.)?(.)?(.)?)( rg6| combo).*(new.*old|old.*new)\b|\bb(.)?l(.)?h t(.)?k(.)?(.)? combo k(a|e)(.)?\b|\bguna(kan)? router dan moderm.*combo\b|\b1-\d{10,12}.*(router|rg|modem).*(rg6*|unc*).*mesh\b|\b(.)?tt.*close.*cpe.*tuka(r)?.*e(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)? 2.5(.)?\b|^(?!.*o(.)?der).*?\b(t(.)?k|x)(.)?((.)?(.)?l(.)?h).*t(.)?k(.)?(.)?.*(combo|rg(.)?)\b|\benable flag (.)?tt\b|\bcombo.*revert.*rg.*biasa\b|\bp(.)?n(.)?k(.)?r(.)?n.*2.5\b|\br(.)?m(.)?(.)?k.*guna.*combo\b|\bspeed radius.*(.)?bps.*layak(.*combo)?\b|\bnew (unc|rg6)[a-z0-9]+\b.*?\bold (rg|rg6)[a-z0-9]+\b.*?\b1-\d{9,11}\b|\bc(.)?st(.)?m(.)?r.*janji.*combo.*renew\b|\bj(.)?d(.)?(k(.)?n)? (rg|vdsl).*s(.)?b(.)?g(.)?(.)? (r(.)?ut(.)?r|rg)\b|\b1(.)?gb(.)?(.)?.*g(.)?n(.)?.*(combo|cb|cbox)\b|\b(c)?tt.*t(.)?k(.)?r combo.*fl(.)?g.*rg5\b|\b(c)?tt truckroll cpe replacement.*g(.)?n(.)?.*combo\b|\b(.)?tt.*rg5.*((spanms )?radius)?.*300(m(b)?(ps)?)?\b|\b(.)?tt no.*sn new:unc.*sn old:(rg.*|unc.*|vd.*)\b|\bc(.)?st(.)?m(.)?r.*100(.)?mb(.)?(.)?.*(promi(.)?e|j(.)?nji).*t(.)?k(.)?r.*combo\b|\bcust(omer)?.*((di)?janji(kan)?|promi(.)?e) (combo|cb(ox)?).*(pack(age)?|pakej) (.)?(.)?(.)?mb(.)?(.)?\b|\b(cb|combo( box)?).*(c)?tt.*sn router.*combo box baru sn\b|\bcombo biasa t(.)?k(.)?r combo 2g\b|\bcust((.)?m(.)?r)? n(.)?k req(uest)? t(.)?k(.)?r combo\b",
        "TT CPE LOV": r"\bfaulty reason\b|\b(su)?dah s(e)?l(e)?ct (c( )?code|cause code).*(tak|x|tidak)( )?b(o)?l(e)?h done (c)?tt\b|\b(tiada|teda|t(a)?kda|xda) cause code\b|\bt(u)?t(u)?p.*upb\b", # check list faulty reason tak keluar
        "TT Unable to Slot/ Error 400": r"\b((c)?tt)( )?unable to slot((c)?tt)?\b|\bno( appoint)? slot\b|\b(error|err) 400\b|\bmcat\b|\btidak slot\b|\b(tidak|tak|x) (dapat|dpt|boleh) slot\b|\bskill ?set\b|\b(tiada|xda) (dp|dc|cab|fdc|fdp) id\b|\b(1-9\d{10,11}).*(tiada|xda)? slot appt\b|\b(tiada|xda)? slot appt.*(1-9\d{10,11})\b|\bslot (error|err)\b|\b(del|delete) (cab|cabinet|dp|fdp|fdc)\b|\bx ada (dp|cab) id\b|\bslot aptt\b|\bwork type\b|\b(tidak|x) auto slot\b|\bctt tiada slot\b|\bappoint err(or)?\b|\baptt error\b|\b(add|tambah) (cab|dp|cabinet) u(n)?t(u)?k map((p)?ing)?\b|\bxleh slot\b|\btiada slot (u(n)?t(u)?k) (slot|appt|appointment)\b|\bmissing granite info.*(appt|appointment|appmnt)?\b|\bctt.*(tiada|xda|xde) slot\b|\badd id\b|\bskill( )?set\b|\bx( )?k(e)?luar book (appt|appmnt|appointment) time\b|\berr(or)? u(n)?t(u)?k slot(ting)?\b|\b(appt|appointment|appmnt) slot.*err(or)?\b|\b(c|k)ab(inet)? id.*d(a)?l(a)?m tm( )?f(orce)?\b|\b(no|tiada) slot\b|\b(c)?tt err(or)?( nak)? slot\b|\b(c)?tt.*(ra|a(p)?(p)?(o)?(i)?(n)?(t)?(m)?(e)?(n)?(t)?) (t(a)?k|x)( )?b(o)?l(e)?h\b|\be(r)?r(o)?r 400\b|\b(c)?tt.*(book|slot).*(a(p)?(p)?(o)?(i)?(n)?(t)?(m)?(e)?(n)?(t)?)\b|(tak|x) k(e)?lua(r)? n(a)?k (book appt|reapp(t)?|ra)|\be(r)?(r)?(o)?(r)? 4(0)?(0|4)?\b|\b(book)?.*app(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?.*(c|k)ab(inet)? mapping\b|\ba(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)? err(.)?(.)?\b|\b(c|k)ab(inet)?.*(t(.)?k|x)( )?(.)?d(.)? d(.)?l(.)?m list\b|\b(.)?tt.*err(..)?.*slot\b|\be(.)?(.)?(.)?(.)?(.)? 400\b|\b(.)?tt.*(fd(p|c)|(c|k)ab(inet)?) id.*assi(.)?(.)? team\b|\bno app(.)?(.)?(.)?t(.)?(.)?(.)?(.)? slot\b|\bbook(ed)? ap(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)? fail(.)?(.)?( cab(inet)?)\b|\b(.)?etul(kan)? ((.)?ab(inet)?|fd(.)?)\b|\b(x|tidak|tak|tdk).*bole(.)?.*slot\b|\b((.)?ab(inet)?|fd(.)?).*ada.*(tidak|tak|x|tdk).*slot\b|\b(.)?tt.*tak n(.)?mp(.)?k slot\b|\b(tidak|x|t(.)?k) b(.)?l(.)?h book (appt|appointment) utk (.)?tt\b",
        "TT Missing/ Update Network Details": r"\b(tiada|xda|tidak ada) detail (cab|dp|fdp|fdc)\b|\bmissing (cab|cabinet|fdc|fdpp|cab|dc|dp)( id\/(dp )?(id)?)?\b|\bexchange (sbnr|sebenar)\b|\bbuang (dp|cab|cabinet).*(c)?tt\b|\b(cab|cabinet|dp|fdp) id null\b|\btiada slot.*( appear)?( cab| cabinet)\b|\btiada dp/cabinet detail\b|\bupdate (dp|cab|cabinet) id\b|\bupdate granite\b|\bbantu..tiada kabinet id\b|\b(dp|cab|cabinet) melek(a)?t\b|\badd mapping( zon(e)?)?\b|\bprovide (dp|cab) id\b|\bbantuan add (cab|cabinet|dp)\b|\bmohon( betulk(a)?n)? dp id\b|\bmohon provide cab( ?/dp)? id\b|\b(mohon )?(update|updte|updt) detail (cab|cabinet|fdp|dp)\b|\btiada m(a)?kl(u)?mat network\b|\b(c)?tt( hsba)? xda(a)? (cab(inet)?|(f)?dp) id\b|\b(c)?tt( hsba)? (xd(a)?|tiada) ((f)?dp|cab(inet)?) id\b|\bmohon bantu buang dp id\b|\b((f)?dp|cab(inet)?) id (xd(a|e)?|tiada)\b|\b(cab(inet)?|(f)?dp) (tiada|xd(a|e)) d(a)?l(a)?m list\b|\bbantuan add c(a)?b(i)?(n)?(e)?t( missing| h(i)?l(a)?(n)?g)?.*(primary|secondary)\b|\berr((o)?(r)?|.*) 400\b|\bmohon betul((a)?(k)?(n)?|.*) (k|c)ab(inet)? id\b|\bupdate detail ((f)?dc|(c|k)ab|(c|k)abinet)\b|\bbetul.*building.*((f)?dc|(c|k)ab|(c|k)abinet)\b|\bbantu retrigger cab/dp\b|\bretrigger.*update cab/dp id\b|\bd(a)?l(a)?m portal (c)?tt (under|b(a)?w(a)?h) (..|...) t(a)?p(i)? (cab(inet)?|kab(inet)?|(f)?dp) (under|b(a)?w(a)?h)\b|\b(add|t(a)?mb(a)?h) (cab(inet)?|kab(inet)?) (..._....(.)?)\b|\bbantu(an)? (ch(e)?(c)?k|sem(a)?k(an)?).*tt.*di (cab(inet)?|kab(inet)?) m(a)?n(a)?\b|\b(c)?tt.*(x|t(a)?k)( )?(d(a|e))? (cab(inet)?|kab(inet)?) ((d(e)?t(a)?(i)?l)|info)\b|\b((f)?dp|(c|k)ab(inet)?) id (x|not|tak)( )?appear\b|\bupdate details ((f)?d(p|c)|(c|k)ab(inet)?)\b|\bsemak (c)?tt.*..._....\b|\b(c)?tt.*((c|k)ab(inet)?).*((x|tak)( )?d(a|e)) d(a)?l(a)?m mapping\b|\bregion dah mapping\b|\bmohon upd(a)?t(e)? ((f)?d(c|p)|cab(inet)?)\b|\b(betulkan|upd(a)?t(e)?) (f)?dp id\b|\bupd(a)?t(e)? (c)?tt.*ke .*dp.*\s\b|\badd (cab(inet)?|(f)?dc).*twu_[a-zA-Z0-9]+\b|\bdapat( )?(kan)? ((f)?d(p|c)|(c|k)ab(inet)?) id\b|\b(c)?tt (tid(a)?k|t(a)?k|x)( )?d(a)?p(a)?t book ap(p)?(o)?(i)?(n)?(t)?(m)?(e)?(n)?(t)?\b|\b((c)?tt)?.*(tiada|teda|takd(a|e)) (c|k)ab(/id)?\b|\bbuang.*p(a)?d(a)? col(umn)? (c|k)ab(inet)?.*(c)?tt\b|\bxd(e|a) ((f)?d(p|c)|(c|k)ab(inet)?) id\b|\bb(e)?t(u)?lk(a)?n ((f)?d(p|c)|(c|k)ab(inet)?) id\b|\bbetul( )?(kan)? (c|k)ab(inet)?( )?id\b|\b((x|tia)da|tak( )?d(a|e)) cab.*dp\b|\bslot date (x|t(a)?k) (ap(p)?ea(r)?|m(u)?nc(u)?l)\b|\badd.*d(a)?l(a)?m.*((c|k)ab(inet)?|fd(c|p))\b|\b(c)?tt (tiada|xd(a|e)) .ab(inet)?\b|\bb(a)?(n)?t(u)?(a)?n upd(a)?(t)?e (fd.|.ab(inet)?).*k(e)?p(a)?d(a)?\b|\bmapping sudah buka\/team id.*n(a)?mp(a)?k\b|\b(c)?tt.*(tiada|((t(a)?k|x)( )?(a)?d(a|e))) id (c|k)ab(inet)?\b|\bgranite (mis(.)?ing|h(i)?l(a)?(n)?g)\b|\b(upd(a)?(t)?(e)?|b(e)?t(u)?lk(a)?n) ((f)?d(p|c)|(c|k)ab(inet)?)\b|\b(tiada|xd(a|e)|teda) (fdp|fdc|(k|c)ab(inet)?) id\b|\bde(.)?(ete)?.*(fdp|fdc|(k|c)ab(inet)?) id\b|\badd.*(c|k)ab(inet)? id\b|\b(c|k)ab(inet)?.*id(.)?dp.*id(.*missing)?\b|\b(tiada|(tak|x)d(a|e)|).*(f)?dp.*((c|k)abinet.*)?id\b|\b((c|k)ab(inet)?).*out.*of.*bound(ary)?\b|\bbuang.*((f)?dp|(c|k)ab(inet)?).*id(\/olt)?.*id\b|\bbantuan upd(.)?(.)?(.)? gr(.)?n(.)?t(.)?\b|\bcabinet \/ fdc \/ dp\b|\btolak ke next\b|\b(building|cab|fdc).*di.*t(.)?p(.)?.*di\b|\bteam t(.)?k(.)?r (.)?d(.)?.*gr(.)?n(.)?t(.)?\b|\bmasuk(kan)? ((c|k)ab(inet)?|fd(.)?) id\b|\b(xd(.)?|tiada|teda) detail ((.)?ab(inet)?|(f)?d(.)?)\b|\b(c)?tt (..|...|....) t(.)?p(.)? ((c|k)ab(inet)?|(f)?d(c|p))( id)?( zon)?\b|\bsalah (.)?d(c|p).*site.*tm(.)?f(orce)?\b|\bbantuan t(.)?k(.)?r(.)?(k(.)?n)? building id dari.*ke(p(.)?d(.)?)?\b",
        "TT V1P": r"\b(ctt |tt )?v1p\b|\b(ctt |tt )?whp\b|\bappt @ \d{3,4}(pm|am)?\b|\b(appt|appmnt|appointment)\.\d{1,2}(\.\d{2})?\b|\b(appt|appmnt|appointment)\s+(pkul\s?)?\d{1,2}\.\d{2}\b|\bvip\b|\b(?:ra|appointment|appt|appmnt)\s*\d{1,2}[:.]\d{2}\s*(?:am|pm)?\b|\bslot.*?\b1-2\d{9,11}\b(?!\d)|\b1-2\d{10,11}.*slot.*(?:[01]?\d|2[0-3])[:.]?[0-5]\d(?:[ap]m)?\b|\b(c)?tt.*1-2\d{9,10}\b @|\b(1-2\d{9,10})( mohon)?(.*ra|.*book).*(1-2\d{9,10})?(am|pm)\b|\b1-2\d{9,10} mohon(.*ra|.*book).*(am|pm)\b|\bb(a)?nt(u)?(a)?n(.*ra|.*book).*(am|pm)( 1-2\d{9,10})\b|\b1-(2)\d{10,11}.*appt (p)?(u)?(k)?(u)?(l)?.*\d{1,3}(.)?(\d{2})?(am|pm)\b|\b(appoin(t)?ment|ap(p)?mnt|appt).*1-(2)\d{10,11}.*\d{3,4}(pm|am)\b|\b1-2\d{10,11}.*m(o)?h(o)?n (appt|appmnt|apt).*\d\b|\b(appointment|appmnt|appt)\s+jam\s+\d{1,2}\.\d{2}(am|pm)\s+1-2\d{10,11}\b|\ba(p)?(p)?(o)?(i)?(n)?(t)?(m)?(e)?(n)?(t)?(k(a)?n)?.*(1-2)\d{10,11}\b|\b1-2\d{10,11}.*(c|k)ab(inet)? id (tak|x)( )?k(e)?l(u)?(a)?(r)?.*r(e)?t(u)?(r)?n next\b|\b1-2\d{9,11}.*appointment.*\b\d{1,2}\.\d{2}\b|\b1-2\d{9,11}.*appt\b|\b1-2\d{9,10}.*app(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?.*p(.)?k(.)?l \d{1,2}(\.)?\d{2}((a|p)m)?\b|\bra p(.)?k(.)?l.*1-2\d{10}\b|\bttv1p\b|\bbantuan slot (.)?(.)m\b|\bui.*(b(.)?rj(.)?y(.)?|d(.)?p(.)?t|d(.)?h) scan sim.*verify.*(t(.)?k|x|t(.)?d(.)?k) b(.)?l(.)?h t(.)?k(.)?n\b|\b1-2\d{10} \d(a|p)m\b|\bra (.)?tt 1-2\d{10}.*p(.)?k(.)?l.*\d{1,2}.\d{1,2}(.)?(a|p)m\b",
        "TT CPE Not Tally with Physical": r"\bclose?d\b.*\b(cpe|mesh|wifi|rg|modem|router)\b(?!.*\bnew (rg|router|wifi|mesh|btu|sp|service point)\b|\bs\/?n baru\b)|\b(tak|x)?sama (dengan|dgn) (fizikal|physical|site)\b|\bxbole(h)? close (c)?tt\b|\bs(/)?n onu d(a)?l(a)?m tmf (tak|x) (sma|sama) d(e)?g(a)?n s(/)?n (d)?(e)?kat fizikal\b|\bupd(a)?t(e)?.*(physical|fizikal)\b|\b(tiada|xd(a|e)?).*d(e)?k(a)?t.*site.*ad(a)?\b|\b(pckg|pakej|package).*(ada)?.*(tmf|tmforce).*(xd(a|e)|tiada)\b|\bpremise.*ada.*(tmf|tmforce|tm force).*(tiada|takda|xda|xde)\b|\bmohon update equipment dalam tm( )?force\b|\bc(u)?st(o)?m(e)?r (i)?ni(e)? ada.*d(a)?l(a)?m tm( )?f(orce)? (tiada|xd(a|e)|takda)\b|\bservice point takde onu tak nampak\b|\bx( )?s(a)?m(a)?.*fizikal.*tm( )?f(orce)?\b|\bdekat site.*ada (mesh|rg|wifi|modem|btu|sp|service point)\b|\bs(/)?n.*(tak|x)( )?s(a)?m(a)?.*fizikal.*tm( )?f(orce)?\b|\badd(kan)? (equipment|eqp|eqmnt) (onu|...|..|service point|....)\b|\bup(d)?(a)?t(e)? s(\/)?n( )?( )?(..|...|....).*(t(ia|e)da|(x|t(a)?k)d(a|e)) d(a)?l(a)?m list e(q)?(u)?(i)?(p)?(m)?(e)?(n)?(t)?\b|\b(onu|btu|sp|service point)?( )?(tiada|teda|x( )?(a)?da) d(a)?l(a)?m tm( )?f(orce)?\b|\b((no|nombor) siri|sn(#)?) (combo box|eq(u)?(i)?(p)?(m)?(e)?(n)?(t)?) s(a)?m(a)?\b|\bb(a)?r(a)?(n)?g.*si(t|d)e.*tm( )?f(orce)? (x|t(a)?k)( )?s(a)?m(a)?\b|\bd(a)?l(a)?m s(i)?(s)?(t)?(e)?m (t(i)?(a)?da|xd(a|e)) (onu|...|..)\b|\bd(a)?l(a)?m tm( )?f(orce)? (tiada|t(a)?kd(a|e)|xd(a|e))( detail)? (modem|..|...|....)\b|\b(tiada|t(a)?kd(a|e)|xd(a|e)) (..|...|....) (d(a)?l(a)?m|d(e)?k(a)?t) tm( )?f(orce)?.*(physical|fizikal).*ada\b|\b(add|t(a)?mb(a)?h)kan (..|...|....|service point)\b|\bminta (t(a)?mb(a)?h|add).*(service point|sp|btu) d(a)?l(a)?m tmf(orce)?\b|\b100mbps.*(onu|btu|sp|service point).*tm( )?f(orce)?.*ada( )?(wifi)?rg\b|\b(s(/)?n) fizikal( )?(:)?( )?(unc|mt|wfh|rg6|rgx|hp|com|uon).*\b|\bs(\/)?n cpe baru(:)?(unc|mt|wfh|rg6|rgx|hp|com|uon).*\b|\bs(\/)?n.*(..|...) (t(a)?k|x)( )?s(a)?m(a)?.*s(\/)?n.*(..|...)?.*site\b|\btab.*f(i)?z(i)?k(a)?l.*((c)?tt)?.*t(u)?t(u)?p( (c)?tt)?\b|\bupd(ate)? s(\/)?n.*(..|...).*tm( )?f(orce)?\b|\blanggan (..|...|....).*eq(.)?(.)?(.)?(.)?(.)?(.)?(.)?\b|\br(u)?m(a)?h.*ada.*mesh.*tm( )?f(orce)?\b|\be(q)?(u)?(i)?(p)?(m)?(e)?(n)?(t)?.*tm( )?f(orce)?.*(tak|x)( )?s(a)?ma\b|\b(sn(#)?|serial no).*(tak|x)( )?sama.*(site|r(u)?m(a)?h)\b|\b(..|...|....|.....) missing d(.)?l(.)?m eq(.)?(.)?(.)?(.)?(.)?(.)?(.)?\b|\bt(.)?(.)?(.)?(.)?(.)?g add (serial( n(o|um))?|sn)( ..| ...| ....| .....) lama\b|\b(add|t(.)?(.)?(.)?(.)?h).*(..|...|....|.....).*d(.)?l(.)?m.*list.*cpe\b|\b(add|t(.)?mb(.)?h) s(.)?n( )?(..|...|....|.....)?( )?lama.*nak update cpe\b|\b(.)?(.)?(.)?(.)?(.)?.*d(.)?l(.)?m list.*(.)?tt\b|\badd.*e(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?.*s(\/)?n\b|\bspeed.*100.*(te)?t(.)?p(.)?.*combo\b|\bflag.*100.*b(.)?l(.)?h.*(rg6|combo)\b|\bt(.)?mb(.)?h sn(.)? (..|...)\b|\bd(.)?l(.)?(.)?(.)? (..|...|....).*(speed|package|pakej)\b|\bt(.)?k(.)?r.*rg.*(.)?(.)?ps.*combo\b|\berror t(.)?k(.)?(.)? rg(.)?\b|\b(tiada|xd(.)?) cpe (..|...)\b|\b(add|tambah)\b|\badd (onu|btu|sp) sn\b|\bt(.)?k(.)?r flag d(.)?r(.)? uonu ke rg\b|\b(btu|sp|modem).*(xda|tidak ada|tiada|tkda).*d(.)?l(.)?m list\b|\bverify.*package(.)?.*c(.)?st(.)?m(.)?r.*r(.)?q(.)?(.)?st\b|\bsite.*ada.*t(.)?p(.)?.*tm(.)?f(orce)?.*(tiad(.)?|xd(.)?|teda|tkd(.)?|tidak ad(.)?)\b|\bupd(.)?(.)?(.)? cpe u(.)?t(.)?k (.)?tt\b|\b(.)?tt.*b(.)?l(.)?(.)?.*close.*cpe\b|\brg(.)?.*t(.)?p(.)?.*cpe.*(comb(.)?(.)?|cb(.)?(.)?|cb)\b|\b100mbps t(.)?p(.)? d(.)?k(.)?t (fizikal|site).*(rg6|combo)\b|\btiada (m(.)?kl(.)?m(.)?t|info|d(.)?t(.)?(.)?l).*rg.*eq(.)?(.)?p(.)?(.)?(.)?(.)?\b|\b(.)?tt.*100mb(.)?(.)?.*new:vd.*(old:)?(.)?rg(.)?\b|\bsn.*(x|t(.)?d(.)?k|t(.)?k) s(.)?m(.)?.*(site|physical|f(.)?z(.)?k(.)?l)\b|\bresolve(.)?.*(.)?tt.*eq(.)?(.)?(.)?(.)?m(.)?(.)?(.)?.*(service point|sp|btu|rg) detect(.)?(.)? mesh(wifirg6)?\b|\bbuang mesh d(.)?l(.)?m eq(.)?(.)?p(.)?(.)?(.)?(.)?.*t(.)?k(.)?r (router|rg)\b|\b(c)?tt.*(close(.)?|resolve(.)?).*((.)?(.)?m(.)?h).*(tiada|x(.)?(.)?d(.)?(.)?|tak(.)?d(.)?) (..|...|....)\b|\bfizikal ada.*t(.)?p(.)?.*tm(.)?f(orce)?.*(cb|combo)\b|\bupdate sn rg6 lama (di)?(.)?(swift|tm(.)?f(orce)?)\b",
        "TT Link LR Appear TMF": r'\bctt link lr appear tmf\b|\b(next )?ntt linkage\b|\bexternal list|ext list\b|\bappear di tmf\b|\bctt under lr\b|\breturn l(a)?ma t(a)?p(i)? m(a)?s(i)?h ada d(a)?l(a)?m (tmf|tm( )?force)\b|\bctt not appear in tm( )?f(orce)? l(e)?p(a)?s (un)?link (ntt|lr)?\b|\bmasih ada di tmf.*lr.*\b|\b(c)?tt link lr\b|\b(c)?tt.*(manual task|mt).*ada di tm( )?f(orce)?\b|\b(c)?tt.*link(ed)?.*lr.*m(.)?s(.)?h appear.*tm( )?f(orce)?\b|\bctt link with lr.*appear.*tm(.)?f(orce)?\b|\b(.)?tt.*appear.*(next.*|mt.*|manual task.*)(.)?remove\b|\b(.)tt.*handle as single (.)?tt.*ada (di( d(.)?l(.)?m)?|d(.)?k(.)?t) tm(.)?f(orce)?\b|\b(.)?tt dah link lr masih appear\b|\b(c)?tt link(ed)?.*lr ada.*tm(.)?f(orce)?\b',
        "TT Blank Source Skill": r'\b(blank )?source skill( blank)?\b|\b(tiada|t(a)?k|x( )?(a)?d(a|e)) act(.)?(.)?(.)?(.)?(.)? type\b',
        "ID Locking/ Unlock/ 3rd Attempt": r'\bunlock id\b|\b(pass|pw|password|pwd).*(betul|btl|btul)\b|\b(tak|tk) (boleh|blh) login\b|\b(x|tak|tidak) (dapat|dpt) login\b|\b(?:fail(?:ed)?)\s*(?:log[ -]?in|login|sign[ -]?in|masuk|msk)\b|\bfailed to log in\b|\byour login has been locked after 3 attempts\b|\btmf kena blo(c)?k\b|\bid lock(ed)?\b|\bxbole(h)? login\b|\b(mohon|mhn)\s*(bantuan|bntn|bntuan)\s*(tm\d{5}|q\d{6})\b|\b(tak|x) (blh|boleh) (masuk|msk) tmf\b|\b(x( )?|tak( )?)(boleh|blh).*log( )?in.*tmf\b|\bunlock( )?(semula)?( )?id\b|\bid.*lock(ed)?\b|\b(tidak|tak|x) d(a)?p(a)?t log( )?in\b|\bk(e)?na lock(ed)? 3 attempt fail(ed)?\b|\bxleh log in.*id\b|\b(tidak|x|tak)( )?(boleh|dapat) login tm( )?f(orce)?\b|\b(ui|ru) (tak|x) d(a)?p(a)?t m(a)?s(u)?k tm( )?f(orce)?\b|\bid.*(t(i)?(d)?(a)?k|x).*tm( )?f(orce)?\b|\bid.*(t(a)?k|x) d(a)?p(a)?t login\b|\btm( )?f(orce)?.*lock\b|\b(tidak|x|tak) d(a)?p(a)?t m(a)?s(u)?k tm( )?f(ouce|orce)? mobile\b|\blog( )in fail(ed)?\b|\b(x|tak|tidak) b(o)?l(e)?h.*log( )?in\b|\bg(a)?g(a)?l log( )?in\b|\bid( team)? x(ley|.....) login\b|\bun(-)?blo(c)?k id\b|\bid ui k(e)?n(a)? (b)?lo(c)?k(ed)?\b|\b(t(a)?k|x)( )?(b)?(o)?l(e)?h login\b|\b(ru|ui|installer).*(c|k)(l)?i(.)?k.*un(.)?lock\b|\b(.)?id.*lock(ed)?(.*(tm(.)?f(orce)?|mobile|app|tab))\b|\breset p(.)?(.)?(.)?w(.)?(.)?d (ui|ru)\b|\bunlock( tm(.)?f(orce)? )id\b',
        "TT Unsync": r"\btmf resolv(?:ed)?\b.*\bnova (in[- ]?progress|ip)\b|\bclearkn tmf[.,]?\s*nova cancelled\b|\bcleark(a)?n tmf\b|\b(c)?tt unlink(ed)? from ntt\b|\bopen.*tm( )?f(orce)?.*nova cancel(led)?\b|\bctt d(a)?l(a)?m nova.*done.*d(a)?l(a)?m tm( )?f(orce)?.*open\b|\bbantu clear( )?(kan)? tm( )?f(orce)?.*nova (cancel(led)?|close(d)?)\b|\btmf open.*icp/next closed\b|\btrigger(k(a)?n)? (c)?tt\b|\b(c)?tt unsync(h)?(ed)?\b|\b(c)?tt.*cancel.*nova.*cancel di tm( )?f(orce)?\b|\bcancel (activity|xtvt|aktiviti|actvty).*(c)?tt\b|\bnova status cancel(led)? t(a)?p(i)? tm( )?f(orce)? m(a)?s(i)?h appear(red)?\b|\b(c)?tt.*unsynch(ed)? tm( )?f(orce)? resolve(d)?\b|\breturn(ed)? t(a)?p(i)? (x|t(a)?k)( )?h(i)?l(a)?(n)?g.*m(a)?s(i)?h.*d(a)?l(a)?m tm( )?f(orce)?\b|\b(c)?tt.*cancel(led)? t(a)?p(i)? m(a)?s(i)?h app(e)?(a)?r d(a)?l(a)?m tm( )?f(orce)?\b|\b(c)?(t)?(t)?.*resolve(d)?.*m(a)?(s)?(i)?(h)? open\b|\b(re)?( |-)?trigger.*(c)?tt\b|\bclose(d)?.*tm( )?f(orce)?.*(icp|nova).*(close(d)?|un( |-)schedule(d)?)\b|\btm( )?f(orce)?.*close(d)?.*(icp|nova).*(close(d)?|un( |-)?schedule(d)?)\b|\bopen.*tm( )?f(orce)?.*(nova|icp) close(d)?\b|\b(c)?tt.*cancel(led)?.*nova.*t(a)?p(i)?.*open.*tm( )?f(orce)?\b|\b(c)?tt.*resolved s(e)?j(a)?k\b|\b(c)?tt.*resolve(d)?.*appear.*tm( )?f(orce)?\b|\b(c)?tt.*done.*t(.)?(.)?(.)?(.)?(.)?.*ada.*tm( )?f(orce)?\b|\b(.)?tt.*cancel(led)?.*nova.*(te)?t(.)?p(.)?.*di tm( )?f(orce)?\b|\bnova.*schedule(.)?.*swift.*(pending verify|..)\b|\bnova cancel(...)?.*tm(.)?f(orce)? open.*sync(kan)?\b|\bnova.*(ip|inprogress).*tm(.)?f(orce)?.*(resolve(d)?|close(d)?)\b|\b(c)?tt unsyn(.)?\b|\b(sync(.)?(.)?.*)?ctt.*tmf resolved\b|\bj(.)?d(.)?(k(.)?n)?.*assi(.)?(.)?.*salah\b|\b(.)?tt not sy(.)?(.)?(.)?\b|\bopen.*tmf.*nova done\b|\bclear(.)?(.)?(.)?.*(.)?tt.*unsync(.)?(.)?(.)?\b|\b(.)?tt.*cancel(.)?(.)?(.)?.*nova.*cancel.*tmf(.)?(.)?(.)?(.)?\b|\bubah s(.)?mula (.)?tt.*k(.)?p(.)?d(.)?\b|\bclear(kan)?.*(.)?tt.*nova.*(close(.)?|cancel(led)?)\b|\bclear(kan)? tm(.)?f(orce)? nova (close(.)?|cancel(led)?)\b|\b(.)?tt.*dah close.*m(.)?s(.)?h.*open\b|\b(.)?tt.*(act|akt|xtvt|activity|aktiviti).*nova.*ada\b",
        "TT Missing": r"\bada (dalam|dlm|dekat|dkt) nova (tapi|tp) (tiada|xda|takda) (dalam|dlm|dekat|dkt) tmf\b|\b(retrigger|trigger) ctt\b|\bada dlm nova tp x de dlm tmf\b|\bctt missing\b|\bctt tiada dalam tmf\b|\bm(o)?h(o)?n (re)?(-)?trigger.*(missing|h(i)?l(a)?(n)?g) d(a)?l(a)?m (act(ivity)?|xtvt|aktiviti) list\b|\btt.*appear(kan)? d(a)?l(a)?m tm( )?f(orce)?\b|\b(c)?tt h(i)?l(a)?(n)?g.*tm( )?f(orce)?\b|\b(.)?tt.*m(.)?s(.)?k.*tm( )?f(orce)?\b|\b((.)?tt)?.*er(.)?(.)?(.)? 500\b|\b(.)?tt.*(tiada|xd(a|e)teda).*tm(.)?f(orce)?\b|\b(c)?tt.*que(.)?(.)?.*m(.)?n(.)?\b|\b(.)?tt.*que(.)?(.)?.*(act|activity|aktiviti|(.)?tvty|a(.)?(.)?(.)?(.)?(.)?(.)?(.)?) list\b|\b(.)?tt.*show.*portal.*team\b|\b(.)?tt.*(missing|hilang).*list tm(.)?f(orce)?\b|\bmissing (.)?tt\b|\b(.)?tt.*missing.*tm(.)?f(orce)?\b|\b(.)?tt.*appear.*tm(.)?f(orce)?( portal)?\b|\bappear(.)?k(.)?n( s(.)?m(.)?la)?(.)?(.)?tt.*b(.)?l(.)?m m(.)?nc(.)?l\b",
        "TT Update DiagnosisCode": r"\bdiagnosis( missing| unsync)\b|\b(rno|fs) troubleshooting\b",
        "TT Granite Network Info Error": r"\bcamelia detect data no found\b|\b(tidak|tak|x) dapat pas(s)?( ke)? next\b|\b(c)?tt (x( )d(a|e)|tiada) (m(.)?kl(.)?m(.)?t|info) granite\b|\bgr(.)?n(.)?(.)?(.)? (tiada|x(.)?ad(.)?|xd(.)?) info\b",
        "TT HSBA Reappointment": r"\bappt( ctt)? hsba\b|\b(1-[8|9]\d{10,11})?.*patch( )?( )?(appointment|appt|ctt).*(1-[8|9]\d{10,11})?\b|\bpatch.*a(p)?(p)?(o)?(i)?(n)?(t)?(m)?(e)?(n)?(t)?.*(\d{2}/\d{2}/\d{4})\s*@\s*(\d{1,2}:\d{2}:\d{2}\s*[ap]m)\b|\b.patch.*a(p)?(p)?(o)?(i)?(n)?(t)?(m)?(e)?(n)?(t)?.*\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}:\d{2} (am|pm)\b|\bpatch.*\d{2}/\d{2}/\d{4}\s\d{1,2}:\d{2}(?::\d{2}\s(?:am|pm)|(?:\s|$))|\bslot (.)?tt hsba\b|\bappt nova\b|\bmohon patch slot on (\d{1,2}/\d{1,2}) @ (\d{1,2}(am|pm))\b|\bbantu patch dlm tmf ctt (1-\d{10,12}) (\d{2}/\d{2}/\d{4}) @ (\d{2}:\d{2}:\d{2} (?:am|pm))\b|\bslot(.)?k(.)?n (appmt|app(.)?(.)?(.)?(.)?(.)?(.)?(.)?(.)?).*(.)?tt hsba.*(am|pm)\b|\b1-\d{10,12}.*\d{1,2}\/\d{1,2}\/\d{2,4} \d{1,2}:\d{1,2}:\d{1,2} (.)?m\b|\b1-\d{10,12}.*patch slot \d{1,2}\/\d{1,2}\/\d{2,4} @\d{1,2}.\d{1,2}(.)?m\b",
        "TT Invalid Activity Type": r"\b(ac|x)t(i)?v(i)?t(y)? t(y)?p(e)? (s(a)?l(a)?h|inv(a)?lid)( )?(route|l(e)?t(a)?k|assign(ed)?)?\b|\bdel(ete)?.*(act|activity|xtvt|aktiviti).*rno\b",
        "Resource Management Issue": r"\bsalah zone id\b|\b(manual task|mt) (t(a)?k|x)( )?d(a)?p(a)?t( nak)?( )?assign\b|\ba(s)?(s)?(i)?(g)?(n)? (mt|m(a)?(n)?(u)?(a)?l t(a)?(s)?(k)?)\b|\b(t(a)?k|x)( )?b(o)?l(e)?h upd(a)?(t)?(e)? c(u)?t(i)?\b|\bmasuk((.)?an)?.*ke(.)?d(.)?l(.)?m.*id\b|\bm(.)?s(.)?(.)? (t(.)?k|x) b(.)?l(.)?h.*a(.)?(.)?ig(.)?.*(id|ui|ru)\b|\bteam.*(access|akses)*tm(.)?f(orce)?\b",
        "TT Duplicated Activity": r"\bc(a)?(n)?c(e)?l dup(licate(d)?)? act(i)?(v)?(i)?(t)?(y)?\b|\bcancel satu a.t(ivity)? a-\d{9,10}\b|\bcancel.*act\b|\bcancel(led)?.*duplicate(.)?.*(activity|xtvt|aktiviti)\b|\bada (2|dua) (act(.)?(.)?(.)?(.)?(.)?(.)?|akt(.)?(.)?(.)?(.)?(.)?|xtvt)\b|\b(.)?tt.*dup(.)?(.)?(.)?(.)?(.)?(.)?.*(activity|aktivity|(.)?(.)?(.)?(.)?)\b|\bcancel (act|akt|activity|aktivity|xtvt).*pending a(.)?(.)?i(.)?(.)?\b|\bcancel(led)?(.)?(act|akt|xtvt|activity|aktiviti).*dup(.)?(.)?(.)?(.)?(.)?(.)? (.)?tt\b|\bremove or cancel(.)?(.)?(.)? a(ct|k)(.)?(.)?(.)?(.)?(.)?\b|\b(.)?tt.*(mempunyai|ada) 2 waktu (app|appointment).*(lain|berbeza)\b|\bcancel salah satu (ac(.)?(.)?v(.)?(.)?(.)?|ak(.)?(.)?(.)?(.)?(.)?(.)?|xtvt) id\b|\b(act(ivity)?|akt(iviti)?|xtvt) dup(licate(.)?)?.*cancel.*satu\b",
        "TT Duplicate CPE SN#": r"\bdup(licate(d)?)? item.*(n(o)?(m)?(b)?(o)?(r)?|n(u)?m(b)?(e)?(r)?) (siri|sn(#)?).*s(a)?m(a|e)\b|\b(n(o)?mb(o)?r|n(u)?mb(e)?r) (siri|sn(#)?).*s(a)?m(a|e)\b|\b(c)?tt.*s(\/)?n dup(licate)?\b|\bdup(licate)? (serial no|sn)( #)?( )?faulty\b|\bduplicate sn( untuk .. (dan|&)( ....)?)?\b|\b(n(o|u)(m)?)(b(e|o)r)? (sn|serial number) s(.)?m(.)?\b|\b(mesh|rg|modem|sp|btu|r(.)?uter).*s(.)?m(.)? d(.)?(.)?(.)?(.)?n.*(mesh|rg|modem|sp|btu|r(.)?uter)\b",
        "TT Expired CPE Warranty": r"\bb(.)?t(.)?l(k(.)?n)?.*warranty.*cpe.*(c)?tt b(.)?r(.)?.*(c)?tt l(.)?m(.)?\b",
        "Invalid TT Info": r"\b(s(.)?m(.)?k|ch(.)?ck) (.)?tt.*s(.)?l(.)?h create.*( create(.)?.*vobb.*s(.)?m(.)?.*c(.)?st(.)?m(.)?r.*(lain|berbeza))?\b",
        "TaaS AOS Not Updated": r"\bstat(us)? (aos|activate(.)?on(.)?site) - n\b"
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
                elif issue == "Order Missing/ Pending Processing" or issue == "Missing Manual Assign Button" or issue == "Patch Combo Flag (AX30002_5G no stock)" or issue == "TT RG6/ Combo Update" or issue == "TT Missing/ Update Network Details" or issue == "TT V1P" or issue == "Release Assign To Me" or issue == "Equipment New to Existing":
                    if tickets:
                        global_result[issue].extend(t for t in tickets if t not in added_tickets)
                        added_tickets.update(tickets)
                else:
                    # For other issues, capture both tickets and IDs
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
                    global_result["Others (to manually add into report)"].extend([(t, message) for t in tickets if t not in added_tickets])
                    added_tickets.update(tickets)
                if ids:
                    global_result["Others (to manually add into report)"].extend([(i, message) for i in ids if i not in added_ids])
                    added_ids.update(ids)

# Function to process all files for categorization (Process 2)
def process_uploaded_files_categorization(uploaded_files):
    global global_result
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
        "Update Customer IC": [],
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
        "Patch Combo Flag (AX30002_5G no stock)": [],
        "Slotted HSBA Order, Remained Returned": [],
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
        "TT Invalid Activity Type": [],
        "Resource Management Issue": [],
        "TT Duplicated Activity": [],
        "TT Duplicate CPE SN#": [],
        "TT Expired CPE Warranty": [],
        "Invalid TT Info": [],
        "TaaS AOS Not Updated": [],
        "Others (to manually add into report)": [] #maybe due to invalid order/ ticket number/ duplicate issues/ standalone ticket/ order numbers/ issue mmg xletak, cuma minta bantuan ja
        #xdeng na 'mohon bantuan followed by order#/ ticket#(no slot) -- kalau tak, langgar dengan issue 'order missing'/ 'full capping'
        #basically masuk 'others', due to NO CONTEXT!
    }

    for uploaded_file in uploaded_files:
        file_contents = uploaded_file.read().decode("utf-8")
        process_messages_from_file(file_contents)

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
    
    # Output the accumulated result
    output = []
    for issue, numbers in global_result.items():
        if numbers:
            output.append(f"{issue}:")
            if issue == "Others (to manually add into report)":
                for number, message in numbers:
                    output.append(f"{number.upper()} - Message: {message}")
            else:
                for number in numbers:
                    output.append(number.upper())
            output.append("")  # Blank line after each issue
    return "\n".join(output)

# File upload for Process 2
uploaded_files_categorize = st.file_uploader("Upload text file for categorization (max 2)", type="txt", accept_multiple_files=True)

# Button to trigger file categorization
if uploaded_files_categorize and st.button('Categorize file contents'):
    categorized_output = process_uploaded_files_categorization(uploaded_files_categorize)
    
    # Display the output in a disabled text area
    st.text_area("Categorized Output", value=categorized_output, height=400, disabled=True)
