import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import quote

# Load or initialize leads data
@st.cache_data
def get_leads_data():
    try:
        return pd.read_csv("leads_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Name", "Email", "Phone", "Source", "Salesperson", "Follow-up Date", "Status"])

leads_data = get_leads_data()

# Function to Generate Calendar Link
def generate_calendar_link(name, follow_up_date):
    start_date = follow_up_date.strftime("%Y%m%dT100000")
    end_date = follow_up_date.strftime("%Y%m%dT110000")
    title = quote(f"Follow-up Reminder: {name}")
    description = quote(f"Reminder to follow up with {name}.")
    calendar_link = f"https://calendar.google.com/calendar/u/0/r/eventedit?text={title}&dates={start_date}/{end_date}&details={description}"
    return calendar_link

# App title
st.title("Lead Management System")

# Load existing data from file (ensures no overwrite)
try:
    existing_data = pd.read_csv("leads_data.csv")
except FileNotFoundError:
    existing_data = pd.DataFrame(columns=["Name", "Email", "Phone", "Source", "Salesperson", "Follow-up Date", "Status"])

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
    leads_data = pd.concat([existing_data, new_lead], ignore_index=True)
    leads_data.to_csv("leads_data.csv", index=False)
    st.success("Lead added successfully!")
    
    # Calendar Link Generation
    calendar_link = generate_calendar_link(name, follow_up_date)
    st.markdown(f"📅 [Click here to create a calendar reminder for {name}]({calendar_link})")
    
    # Suggested WhatsApp Message
    whatsapp_message = f"Hi {name},\n\nPlease click the link below to set a reminder for our follow-up on {follow_up_date}:\n{calendar_link}"
    encoded_message = quote(whatsapp_message)
    whatsapp_link = f"https://wa.me/?text={encoded_message}"
    st.markdown(f"💬 [Send Reminder on WhatsApp]({whatsapp_link})")

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
