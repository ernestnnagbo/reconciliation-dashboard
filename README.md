# Zybs Reconciliation Engine - Streamlit Version

**Version:** 1.0 (Quick Deploy)  
**Built for:** Ernest N, CFO of Zybs Medical Group  
**Date:** December 4, 2025

---

## 🎯 What This Does

This is a **web-based reconciliation dashboard** that performs three-way matching between:
- **Client EOPs** (Explanation of Payments from QTC, VES, OptumServe, Loyal Source)
- **Provider Invoices** (NP, Audiologist, Echo Tech invoices)
- **Sign-in Sheets** (coming in v2)

### Key Features

✅ **Drag-and-drop file upload** (CSV or Excel)  
✅ **Automated matching algorithm** (patient name + service date)  
✅ **Exception reporting** (unbilled revenue, unpaid providers)  
✅ **Financial analytics dashboard**  
✅ **One-click CSV export** of all results  
✅ **AI report generation** (template mode + OpenAI integration ready)  
✅ **DCAA-compliant** audit trail (timestamps, user tracking)

---

## 🚀 Quick Start (3 Options)

### Option 1: Deploy to Streamlit Cloud (Recommended - FREE)

**Step 1:** Create a GitHub account at [github.com](https://github.com)

**Step 2:** Create a new repository called `zybs-reconciliation`

**Step 3:** Upload these files to your repository:
- `reconciliation_app.py`
- `requirements.txt`
- `README.md`

**Step 4:** Go to [share.streamlit.io](https://share.streamlit.io)

**Step 5:** Sign in with your GitHub account

**Step 6:** Click "New App" and select your `zybs-reconciliation` repository

**Step 7:** Click "Deploy"

**Step 8:** You'll get a URL like: `https://zybs-reconciliation.streamlit.app`

**Step 9:** Share this URL with Nicole, Joseph, and your team!

---

### Option 2: Run Locally (For Testing)

**Step 1:** Install Python 3.11+ if you don't have it

**Step 2:** Open Terminal (Mac) or Command Prompt (Windows)

**Step 3:** Navigate to the folder containing these files:
```bash
cd /path/to/zybs-reconciliation-app
```

**Step 4:** Install dependencies:
```bash
pip install -r requirements.txt
```

**Step 5:** Run the app:
```bash
streamlit run reconciliation_app.py
```

**Step 6:** Your browser will open automatically to `http://localhost:8501`

---

### Option 3: Share via Ngrok (Temporary Public Link)

If you want to share your local version with your team temporarily:

**Step 1:** Run the app locally (see Option 2)

**Step 2:** Install ngrok from [ngrok.com](https://ngrok.com)

**Step 3:** In a new terminal, run:
```bash
ngrok http 8501
```

**Step 4:** Ngrok will give you a public URL like `https://abc123.ngrok.io`

**Step 5:** Share this URL with your team (valid for 8 hours)

---

## 📋 How to Use

### Step 1: Upload Files

1. Click the "Upload Files" tab
2. Upload your **Client EOP** CSV/Excel file
3. Upload your **Provider Invoice** CSV/Excel file
4. The app will show you a preview of both files

### Step 2: Map Columns

1. Tell the app which columns contain:
   - **Patient Name** (e.g., "Patient", "Veteran Name", "Full Name")
   - **Service Date** (e.g., "Date of Service", "Exam Date", "DOS")
   - **Amount** (e.g., "Amount Paid", "Total", "Payment")

### Step 3: Run Reconciliation

1. Click the "🚀 Run Reconciliation" button
2. Wait 5-10 seconds while the algorithm runs
3. View results in the "Reconciliation Results" tab

### Step 4: Review Results

The app will show you:

**✅ Matched Records:** Exams that appear on both EOP and Invoice (everything is good!)

**⚠️ Unbilled Revenue:** Exams on EOP but NOT on Invoice (you got paid but have no provider invoice - investigate!)

**🚨 Unpaid Providers:** Exams on Invoice but NOT on EOP (provider is claiming payment but client hasn't paid yet - hold payment!)

### Step 5: Download Reports

Click the download buttons to export:
- Matched records (CSV)
- Unbilled revenue exceptions (CSV)
- Unpaid provider exceptions (CSV)
- Executive summary report (Markdown)

---

## 🔍 Understanding the Results

### Match Rate

**Good:** 90%+ match rate means your processes are working well

**Warning:** 70-89% match rate means you have some process gaps

**Critical:** <70% match rate means serious process failures

### Unbilled Revenue (⚠️)

**What it means:** The client paid you for these exams, but you have no record of paying the provider.

**Why it happens:**
- Provider forgot to invoice
- Invoice was lost or not entered
- Data entry error

**What to do:**
1. Pull the sign-in sheets for these dates
2. Confirm the exams actually happened
3. Get the provider to submit a corrected invoice
4. Pay the provider (you already got paid by the client!)

### Unpaid Providers (🚨)

**What it means:** The provider is claiming payment for exams that don't appear on the client's EOP.

**Why it happens:**
- Exam was rejected by the client
- Exam hasn't been paid yet (5.5 month lag!)
- Provider made a data entry error
- Provider is claiming work they didn't do (fraud risk!)

**What to do:**
1. **HOLD PAYMENT** until you investigate
2. Check the sign-in sheets
3. Check the client portal for rejection reasons
4. Contact the provider to clarify

---

## 💡 Pro Tips

### Tip 1: Standardize Your File Formats

The reconciliation works best when your files have consistent column names. Create templates for:
- QTC EOPs
- VES EOPs
- OptumServe EOPs
- Loyal Source EOPs
- NP Invoices
- Audiologist Invoices
- Echo Tech Invoices

### Tip 2: Run Reconciliation Monthly

Don't wait until year-end! Run this every month to catch issues early.

### Tip 3: Use the Date Tolerance Feature

If your dates are slightly off (e.g., exam on 4/15 but invoice shows 4/16), enable "Date Tolerance" in the sidebar and set it to 1-2 days.

### Tip 4: Enable Fuzzy Matching

If patient names have slight variations (e.g., "John Smith" vs "SMITH, JOHN"), enable "Fuzzy Matching" in the sidebar.

### Tip 5: Save Your Column Mappings

Once you figure out the correct column mappings for each client/provider, write them down! This will save you time next month.

---

## 🔒 Security & Compliance

### HIPAA Compliance

⚠️ **Important:** This Streamlit Cloud version is NOT HIPAA-compliant because:
- Files are temporarily stored on Streamlit's servers
- No encryption at rest
- No BAA (Business Associate Agreement) with Streamlit

**For HIPAA compliance, you MUST:**
- Use Option 2 (run locally on your computer)
- OR wait for next week's full Reconciliation Engine (HIPAA-ready)

### DCAA Compliance

✅ **Audit Trail:** The app timestamps all reconciliations

✅ **Documentation:** All results are exportable for audit purposes

✅ **Transparency:** The matching algorithm is fully documented

⚠️ **Limitation:** This version doesn't track user identity (coming in full version)

---

## 🐛 Troubleshooting

### Problem: "Error reading file"

**Solution:** Make sure your file is a valid CSV or Excel (.xlsx) file. Open it in Excel first to confirm.

### Problem: "No matches found"

**Solution:** Check your column mappings. The patient names and dates must match EXACTLY (or enable fuzzy matching).

### Problem: "App is slow"

**Solution:** Streamlit Cloud has resource limits. If you're processing >10,000 rows, run locally instead.

### Problem: "Can't download results"

**Solution:** Some browsers block downloads. Try a different browser or disable pop-up blockers.

---

## 📞 Support

**Questions?** Contact Ernest N (CFO) at [your email]

**Bug reports?** Create an issue on GitHub

**Feature requests?** We're building the full Reconciliation Engine next week!

---

## 🗓️ Roadmap

### This Week (v1.0 - Streamlit)
✅ Two-way matching (EOP vs Invoice)  
✅ Basic analytics dashboard  
✅ CSV export  
✅ Template reports

### Next Week (v2.0 - Full Engine)
🚧 Three-way matching (+ Sign-in Sheets)  
🚧 Real-time collaboration  
🚧 Database storage (MySQL)  
🚧 User authentication (OAuth)  
🚧 HIPAA compliance  
🚧 Full AI integration (ChatGPT + Gemini)  
🚧 Google Sheets sync  
🚧 QuickBooks integration  
🚧 Mobile app (iOS/Android)

---

## 📄 License

Proprietary - Zybs Medical Group Internal Use Only

---

**Built with ❤️ by Ernest N, CFO**  
**Powered by Streamlit, Pandas, and Python**
