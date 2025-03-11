import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Load or initialize leads data
@st.cache_data
def get_leads_data():
    try:
        return pd.read_csv("leads_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Name", "Email", "Phone", "Source", "Salesperson", "Follow-up Date", "Status"])

leads_data = get_leads_data()

# Generate .ics Calendar File
def generate_ics_file(name, phone, follow_up_date):
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Follow-up Reminder
DESCRIPTION:Don't forget to follow up with {name} at {phone}
DTSTART:{follow_up_date.strftime('%Y%m%dT090000')}
DTEND:{follow_up_date.strftime('%Y%m%dT100000')}
END:VEVENT
END:VCALENDAR
"""
    with open("followup_reminder.ics", "w") as f:
        f.write(ics_content)

    with open("followup_reminder.ics", "rb") as file:
        st.download_button(
            label="📅 Download Calendar Reminder",
            data=file,
            file_name=f"{name}_followup.ics",
            mime="text/calendar"
        )

# App title
st.title("Lead Management System")

# Lead Entry Form
with st.form("lead_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    source = st.selectbox("Source", ["Social Media", "Google", "Walk-in", "Other"])
    salesperson = st.selectbox("Salesperson", ["Joshua", "Joseph", "Nettie"])
    follow_up_date = st.date_input("Follow-up Date", datetime.today() + timedelta(days=3))
    status = st.selectbox("Status", ["New", "Contacted", "Scheduled", "Closed"])
    submit = st.form_submit_button("Add Lead")

if submit:
    new_lead = pd.DataFrame({
        "Name": [name],
        "Email": [email],
        "Phone": [phone],
        "Source": [source],
        "Salesperson": [salesperson],
        "Follow-up Date": [follow_up_date],
        "Status": [status]
    })
    leads_data = pd.concat([leads_data, new_lead], ignore_index=True)
    leads_data.to_csv("leads_data.csv", index=False)
    st.success("Lead added successfully!")

    # Generate .ics file for native calendar
    generate_ics_file(name, phone, follow_up_date)

# Upload leads from spreadsheet
st.subheader("Upload Leads from Spreadsheet")
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
if uploaded_file is not None:
    uploaded_leads = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    required_columns = ["Name", "Email", "Phone"]
    if all(col in uploaded_leads.columns for col in required_columns):
        leads_data = pd.concat([leads_data, uploaded_leads], ignore_index=True)
        leads_data.to_csv("leads_data.csv", index=False)
        st.success("Leads uploaded successfully!")
    else:
        st.error("Uploaded file must contain 'Name', 'Email', and 'Phone' columns.")

# Display leads
st.subheader("Leads List")
if not leads_data.empty:
    st.dataframe(leads_data)
else:
    st.info("No leads yet. Add some leads to get started.")
