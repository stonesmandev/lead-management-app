import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from ics import Calendar, Event

# Load or initialize leads data
def get_leads_data():
    try:
        return pd.read_csv("leads_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Name", "Email", "Phone", "Source", "Salesperson", "Follow-up Date", "Status"])

leads_data = get_leads_data()

# Save leads data
def save_leads_data(data):
    data.to_csv("leads_data.csv", index=False)

# Generate Calendar File
def generate_calendar_file(name, phone, follow_up_date):
    calendar = Calendar()
    event = Event()
    event.name = f"Follow-up with {name}"
    event.begin = follow_up_date.strftime("%Y-%m-%d 09:00:00")
    event.description = f"Follow up with {name} at {phone}"
    calendar.events.add(event)
    
    with open("follow_up_reminder.ics", "w") as f:
        f.writelines(calendar)

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
    save_leads_data(leads_data)
    
    # Create Calendar File
    generate_calendar_file(name, phone, follow_up_date)
    
    st.success("Lead added successfully!")
    st.download_button("📅 Download Calendar Reminder", "follow_up_reminder.ics")

# Upload leads from spreadsheet
st.subheader("Upload Leads from Spreadsheet")
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
if uploaded_file is not None:
    uploaded_leads = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    required_columns = ["Name", "Email", "Phone"]
    if all(col in uploaded_leads.columns for col in required_columns):
        leads_data = pd.concat([leads_data, uploaded_leads], ignore_index=True)
        save_leads_data(leads_data)
        st.success("Leads uploaded successfully!")
    else:
        st.error("Uploaded file must contain 'Name', 'Email', and 'Phone' columns.")

# Display leads
st.subheader("Leads List")
if not leads_data.empty:
    st.dataframe(leads_data)
    # Download Option
    st.download_button("Download Leads", leads_data.to_csv(index=False), "leads_data.csv", "text/csv")
else:
    st.info("No leads yet. Add some leads to get started.")
