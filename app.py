import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from ics import Calendar, Event

# Load or initialize leads data
@st.cache_data
def get_leads_data():
    try:
        return pd.read_csv("leads_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Name", "Email", "Phone", "Source", "Salesperson", "Follow-up Date", "Status"])

leads_data = get_leads_data()

# Generate .ics file for calendar event
def generate_ics_file(name, phone, follow_up_date):
    cal = Calendar()
    event = Event()
    event.name = f"Follow-up with {name}"
    event.begin = follow_up_date.strftime("%Y-%m-%d 09:00:00")
    event.description = f"Don't forget to follow up with {name} at {phone}"
    
    cal.events.add(event)
    
    file_path = f"{name.replace(' ', '_')}_followup.ics"
    with open(file_path, 'w') as f:
        f.writelines(cal)
    
    return file_path

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

    # Generate and download .ics file
    ics_file = generate_ics_file(name, phone, follow_up_date)
    with open(ics_file, "rb") as f:
        st.download_button(
            label="📅 Download Calendar Reminder",
            data=f,
            file_name=ics_file,
            mime="text/calendar"
        )

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
