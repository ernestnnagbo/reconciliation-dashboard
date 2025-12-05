import streamlit as st
import pandas as pd
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Reconciliation Command Center",
    page_icon="📊",
    layout="wide"
)

# --- SHARED DATA MANAGER ---
# This mimics a database to store logs and prompts across users
@st.cache_resource
class StreamlitDataManager:
    def __init__(self):
        self.current_prompt = """Act as a financial auditor. Analyze the following reconciliation data:
        - Total Invoices: {total_invoices}
        - Paid Count: {paid_count}
        - Unpaid Count: {unpaid_count}
        - Total Outstanding Value: ${unpaid_value}
        
        The unpaid/mismatched veterans are: {unpaid_names}.
        
        Please provide a brief executive summary for the finance team regarding the payment status."""
        self.logs = []

    def get_prompt(self): return self.current_prompt
    def update_prompt(self, new_prompt): self.current_prompt = new_prompt
    def log_activity(self, user, action, details=""):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs.insert(0, {"Time": timestamp, "User": user, "Action": action, "Details": details})
    def get_logs(self): return self.logs

data_manager = StreamlitDataManager()

# --- SECURITY / LOGIN SYSTEM ---
USERS = {
    "team": "finance123",   # Team Member Login
    "admin": "admin999"     # Manager Login
}

def check_login():
    if "logged_in_role" not in st.session_state:
        st.session_state["logged_in_role"] = None

    if st.session_state["logged_in_role"] is None:
        st.markdown("## 🔐 Secure Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in USERS and USERS[username] == password:
                st.session_state["logged_in_role"] = username
                data_manager.log_activity(username, "Login", "User accessed system")
                st.rerun()
            else:
                st.error("Incorrect username or password")
        
        st.divider()
        with st.expander("ℹ️ Need Credentials?"):
            st.markdown("**Team:** `team` / `finance123`  \n**Manager:** `admin` / `admin999`")
        return None
    return st.session_state["logged_in_role"]

# --- MAIN APP LOGIC ---
role = check_login()

if role:
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("⚙️ Dashboard")
        st.info(f"👤 User: {role}")
        if st.button("Logout"):
            st.session_state["logged_in_role"] = None
            st.rerun()

    # --- MANAGER VIEW ---
    if role == "admin":
        st.title("🛡️ Manager Command Center")
        t1, t2 = st.tabs(["Logs", "Edit Prompt"])
        with t1: st.dataframe(pd.DataFrame(data_manager.get_logs()), use_container_width=True)
        with t2:
            new_promt = st.text_area("Global Prompt", value=data_manager.get_prompt(), height=300)
            if st.button("Save Prompt"):
                data_manager.update_prompt(new_promt)
                st.success("Updated!")

    # --- TEAM VIEW (Reconciliation) ---
    else:
        st.title("📊 Financial Reconciliation Dashboard")
        st.markdown("### Upload Master EOP and Provider Invoices")

        col1, col2 = st.columns(2)
        with col1: eop_file = st.file_uploader("1. Upload Master EOP", type=['csv'])
        with col2: invoice_file = st.file_uploader("2. Upload Provider Invoices", type=['csv'])

        if eop_file and invoice_file:
            try:
                # Load Data
                df_eop = pd.read_csv(eop_file)
                invoice_file.seek(0)
                df_invoice = pd.read_csv(invoice_file)
                # Header fix
                if 'Veteran Full Name' not in df_invoice.columns:
                    invoice_file.seek(0)
                    df_invoice = pd.read_csv(invoice_file, header=1)

                # --- 1. CLEANING DATA ---
                # Clean Dates
                df_eop['Examdate Clean'] = pd.to_datetime(df_eop['Examdate'], errors='coerce')
                df_invoice['Exam Date Clean'] = pd.to_datetime(df_invoice['Exam Date'], errors='coerce')

                # Clean Names
                df_eop['Last Name Clean'] = df_eop['Examinee Last Name'].astype(str).str.strip().str.upper()
                def extract_last_name(full_name):
                    if pd.isna(full_name): return ""
                    parts = str(full_name).strip().split()
                    return parts[-1].upper() if parts else ""
                df_invoice['Last Name Clean'] = df_invoice['Veteran Full Name'].apply(extract_last_name)

                # Clean VES Case Numbers
                df_eop['Vescase_Clean'] = pd.to_numeric(df_eop['Vescase'], errors='coerce').fillna(0).astype(int).astype(str)
                
                # Check if invoice has VES Case column
                if 'VES Case #' in df_invoice.columns:
                    df_invoice['Invoice_VES_Clean'] = pd.to_numeric(df_invoice['VES Case #'], errors='coerce').fillna(0).astype(int).astype(str)
                    df_invoice['Invoice_VES_Clean'] = df_invoice['Invoice_VES_Clean'].replace('0', '')
                else:
                    df_invoice['Invoice_VES_Clean'] = ''

                # --- 2. WATERFALL MATCHING LOGIC ---
                # A. Set of valid VES Cases
                valid_ves_cases = set(df_eop[df_eop['Vescase_Clean'] != '0']['Vescase_Clean'].unique())
                
                # B. Lookup for Name+Date
                eop_lookup = df_eop[['Last Name Clean', 'Examdate Clean', 'Vescase_Clean']].dropna().drop_duplicates()

                def find_match_status(row):
                    # STEP 1: CHECK VES CASE #
                    inv_ves = row['Invoice_VES_Clean']
                    if inv_ves and inv_ves in valid_ves_cases:
                        return "Paid (Matched VES#)", inv_ves

                    # STEP 2: CHECK NAME + DATE
                    date_matches = eop_lookup[eop_lookup['Examdate Clean'] == row['Exam Date Clean']]
                    if not date_matches.empty:
                        full_name = str(row['Veteran Full Name']).upper()
                        for _, eop_row in date_matches.iterrows():
                            if eop_row['Last Name Clean'] in full_name:
                                return "Paid (Matched Name/Date)", eop_row['Vescase_Clean']
                    
                    # STEP 3: FALLOUT (UNPAID)
                    return "Unpaid / Mismatch", None

                with st.spinner('Running Waterfall Reconciliation...'):
                    results = df_invoice.apply(lambda row: pd.Series(find_match_status(row)), axis=1)
                    df_invoice['Status_Reconciled'] = results[0]
                    df_invoice['Matched_Vescase'] = results[1]

                # Split Results
                paid_df = df_invoice[df_invoice['Status_Reconciled'].str.contains("Paid")]
                unpaid_df = df_invoice[df_invoice['Status_Reconciled'].str.contains("Unpaid")]

                # --- DASHBOARD STATS ---
                st.divider()
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Invoices", len(df_invoice))
                m2.metric("✅ Matched / Paid", len(paid_df))
                m3.metric("⚠️ Mismatch / Unpaid", len(unpaid_df), delta_color="inverse")

                # --- RESULTS TABS ---
                tab1, tab2, tab3 = st.tabs(["⚠️ Mismatches (Unpaid)", "✅ Paid Invoices", "🤖 AI Analysis"])

                with tab1:
                    st.header("Mismatch Report")
                    st.write("These invoices matched neither the VES Case # nor the Name/Date combination.")
                    st.dataframe(unpaid_df, use_container_width=True)
                    csv_unpaid = unpaid_df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Mismatch Report", csv_unpaid, 'mismatches.csv', 'text/csv', type="primary")

                with tab2:
                    st.dataframe(paid_df, use_container_width=True)

                with tab3:
                    raw_template = data_manager.get_prompt()
                    final_prompt = raw_template.format(
                        total_invoices=len(df_invoice),
                        paid_count=len(paid_df),
                        unpaid_count=len(unpaid_df),
                        unpaid_value="[Value]",
                        unpaid_names=', '.join(unpaid_df['Veteran Full Name'].head(5).astype(str).tolist())
                    )
                    st.text_area("Admin Prompt", value=final_prompt, disabled=True)
                    if st.button("Generate Report"):
                        st.info("Simulated AI Report: Status Update - Action required on Mismatches.")

            except Exception as e:
                st.error(f"Error: {e}")
