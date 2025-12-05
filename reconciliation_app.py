import streamlit as st
import pandas as pd
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Reconciliation Command Center",
    page_icon="📊",
    layout="wide"
)

# --- SHARED DATA MANAGER (Simulating a Database) ---
# We use @st.cache_resource to create a "Global" object that persists 
# across different users' sessions on the same server.
@st.cache_resource
class StreamlitDataManager:
    def __init__(self):
        # Default System Prompt
        self.current_prompt = """Act as a financial auditor. Analyze the following reconciliation data:
        - Total Invoices: {total_invoices}
        - Paid Count: {paid_count}
        - Unpaid Count: {unpaid_count}
        - Total Outstanding Value: ${unpaid_value}
        
        The unpaid veterans are: {unpaid_names}.
        
        Please provide a brief executive summary for the finance team regarding the payment status and recommended actions."""
        
        # Activity Log (List of dictionaries)
        self.logs = []

    def get_prompt(self):
        return self.current_prompt

    def update_prompt(self, new_prompt):
        self.current_prompt = new_prompt

    def log_activity(self, user, action, details=""):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "Time": timestamp,
            "User": user,
            "Action": action,
            "Details": details
        }
        # Add to beginning of list (newest first)
        self.logs.insert(0, entry)

    def get_logs(self):
        return self.logs

# Initialize the shared manager
data_manager = StreamlitDataManager()

# --- SECURITY / LOGIN SYSTEM ---
USERS = {
    "team": "finance123",  # Regular User
    "admin": "admin999"    # Manager/Admin
}

def check_login():
    """Simple login system returning the role (team/admin) or None."""
    
    if "logged_in_role" not in st.session_state:
        st.session_state["logged_in_role"] = None

    if st.session_state["logged_in_role"] is None:
        st.markdown("## 🔐 Secure Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in USERS and USERS[username] == password:
                st.session_state["logged_in_role"] = username
                # Log the login
                data_manager.log_activity(username, "Login", "User accessed system")
                st.rerun()
            else:
                st.error("Incorrect username or password")
        return None
    
    return st.session_state["logged_in_role"]

# --- MAIN APP LOGIC ---
role = check_login()

if role:
    # --- SIDEBAR (Common to both) ---
    with st.sidebar:
        st.header("⚙️ Dashboard")
        if role == "admin":
            st.warning("🛡️ ADMIN MODE ACTIVE")
        else:
            st.info(f"👤 User: {role}")
            
        if st.button("Logout"):
            data_manager.log_activity(role, "Logout", "User exited system")
            st.session_state["logged_in_role"] = None
            st.rerun()

    # ==========================================
    #           ADMIN / MANAGER VIEW
    # ==========================================
    if role == "admin":
        st.title("🛡️ Manager Command Center")
        
        admin_tab1, admin_tab2 = st.tabs(["👁️ Team Activity Logs", "✏️ Edit AI Prompt"])
        
        with admin_tab1:
            st.subheader("Live Activity Feed")
            logs = data_manager.get_logs()
            if logs:
                df_log = pd.DataFrame(logs)
                st.dataframe(df_log, use_container_width=True)
            else:
                st.info("No activity recorded yet.")
                
        with admin_tab2:
            st.subheader("Centralized AI Prompt Configuration")
            st.markdown("Edit the prompt below. **All team members will immediately use this new version.**")
            
            current_template = data_manager.get_prompt()
            new_template = st.text_area("Global Prompt Template", value=current_template, height=300)
            
            if st.button("💾 Save Global Prompt"):
                data_manager.update_prompt(new_template)
                data_manager.log_activity("admin", "Update Prompt", "Modified global AI prompt")
                st.success("Prompt updated! All team members will now use this version.")

    # ==========================================
    #           TEAM MEMBER VIEW
    # ==========================================
    else:
        st.title("📊 Financial Reconciliation Dashboard")
        st.markdown("### Upload Master EOP and Provider Invoices")

        # --- FILE UPLOADER ---
        col1, col2 = st.columns(2)
        with col1:
            eop_file = st.file_uploader("1. Upload Master EOP (CSV)", type=['csv'])
        with col2:
            invoice_file = st.file_uploader("2. Upload Provider Invoices (CSV)", type=['csv'])

        # --- RECONCILIATION LOGIC ---
        if eop_file and invoice_file:
            try:
                # Load Data
                df_eop = pd.read_csv(eop_file)
                
                # Smart Header Detection
                invoice_file.seek(0)
                df_invoice = pd.read_csv(invoice_file)
                if 'Veteran Full Name' not in df_invoice.columns:
                    invoice_file.seek(0)
                    df_invoice = pd.read_csv(invoice_file, header=1)

                # Log Upload
                if "upload_logged" not in st.session_state:
                    data_manager.log_activity(role, "Upload Files", f"Invoices: {len(df_invoice)} rows")
                    st.session_state["upload_logged"] = True

                # 1. CLEANING DATA
                df_eop['Examdate Clean'] = pd.to_datetime(df_eop['Examdate'], errors='coerce')
                if 'Exam Date' in df_invoice.columns:
                    df_invoice['Exam Date Clean'] = pd.to_datetime(df_invoice['Exam Date'], errors='coerce')
                
                df_eop['Last Name Clean'] = df_eop['Examinee Last Name'].astype(str).str.strip().str.upper()
                
                def extract_last_name(full_name):
                    if pd.isna(full_name): return ""
                    parts = str(full_name).strip().split()
                    return parts[-1].upper() if parts else ""
                    
                df_invoice['Last Name Clean'] = df_invoice['Veteran Full Name'].apply(extract_last_name)

                # 2. MATCHING LOGIC
                eop_lookup = df_eop[['Last Name Clean', 'Examdate Clean', 'Vescase']].dropna().drop_duplicates()
                
                def find_match_status(row):
                    match = eop_lookup[
                        (eop_lookup['Last Name Clean'] == row['Last Name Clean']) & 
                        (eop_lookup['Examdate Clean'] == row['Exam Date Clean'])
                    ]
                    if not match.empty:
                        return "Paid", match.iloc[0]['Vescase']
                    
                    date_match = eop_lookup[eop_lookup['Examdate Clean'] == row['Exam Date Clean']]
                    if not date_match.empty:
                        full_name = str(row['Veteran Full Name']).upper()
                        for _, eop_row in date_match.iterrows():
                            if eop_row['Last Name Clean'] in full_name:
                                return "Paid (Fuzzy)", eop_row['Vescase']
                    
                    return "Unpaid", None

                with st.spinner('Reconciling accounts...'):
                    df_invoice[['Status_Reconciled', 'Matched_Vescase']] = df_invoice.apply(
                        lambda row: pd.Series(find_match_status(row)), axis=1
                    )
                
                df_invoice['Matched_Vescase'] = df_invoice['Matched_Vescase'].apply(lambda x: f"{int(x)}" if pd.notna(x) else "")
                paid_df = df_invoice[df_invoice['Status_Reconciled'].str.contains("Paid")]
                unpaid_df = df_invoice[df_invoice['Status_Reconciled'] == "Unpaid"]

                # --- DASHBOARD STATISTICS ---
                st.divider()
                total_invoices = len(df_invoice)
                paid_count = len(paid_df)
                unpaid_count = len(unpaid_df)
                
                def clean_currency(x):
                    if isinstance(x, str):
                        return float(x.replace('$', '').replace(',', ''))
                    return float(x) if x else 0.0

                total_value = df_invoice['Invoice Amount'].apply(clean_currency).sum()
                unpaid_value = unpaid_df['Invoice Amount'].apply(clean_currency).sum()

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Invoices", total_invoices)
                m2.metric("Paid / Matched", paid_count, delta=f"{paid_count/total_invoices:.1%}")
                m3.metric("Unpaid / Alert", unpaid_count, delta=f"-{unpaid_count}", delta_color="inverse")
                m4.metric("Outstanding Amount", f"${unpaid_value:,.2f}")

                # --- TABS ---
                tab1, tab2, tab3 = st.tabs(["🔴 Unpaid Invoices", "🟢 Paid Invoices", "🤖 AI Analysis"])
                
                with tab1:
                    st.dataframe(unpaid_df, use_container_width=True)
                    csv_unpaid = unpaid_df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Unpaid CSV", csv_unpaid, 'unpaid_invoices.csv', 'text/csv', type="primary")

                with tab2:
                    st.dataframe(paid_df, use_container_width=True)
                    csv_paid = paid_df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Paid CSV", csv_paid, 'paid_invoices.csv', 'text/csv')

                with tab3:
                    st.markdown("### AI Executive Summary")
                    
                    # FETCH PROMPT FROM GLOBAL MANAGER
                    raw_template = data_manager.get_prompt()
                    
                    # Fill in the dynamic variables
                    unpaid_names_list = ', '.join(unpaid_df['Veteran Full Name'].head(5).tolist())
                    final_prompt = raw_template.format(
                        total_invoices=total_invoices,
                        paid_count=paid_count,
                        unpaid_count=unpaid_count,
                        unpaid_value=unpaid_value,
                        unpaid_names=unpaid_names_list
                    )
                    
                    st.text_area("Generated Prompt (Controlled by Admin)", value=final_prompt, height=200, disabled=True)
                    st.caption("🔒 This prompt structure is managed by the Admin.")
                    
                    if st.button("✨ Generate Report"):
                        # Log the generation event
                        data_manager.log_activity(role, "Generate AI Report", f"Outstanding: ${unpaid_value}")
                        
                        st.info("ℹ️ Using Simulation Mode")
                        st.markdown(f"""
                        **Executive Summary: Reconciliation Audit**
                        *Generated based on Admin Protocols*
                        
                        **Status:** Action Required
                        A total of **{total_invoices}** invoices were processed. Discrepancies were found in **{unpaid_count}** accounts.
                        """)

            except Exception as e:
                st.error(f"Error processing files: {e}")
