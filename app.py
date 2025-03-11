import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage

# Load or initialize leads data
@st.cache_data
def get_leads_data():
    try:
        return pd.read_csv("leads_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Name", "Email", "Phone", "Source", "Salesperson", "Follow-up Date", "Status"])

leads_data = get_leads_data()

# Email Function for Follow-ups
def send_email(name, email, follow_up_date):
    try:
        msg = EmailMessage()
        msg['Subject'] = "Follow-up Reminder"
        msg['From'] = "your_email@gmail.com"  # Replace with your email
        msg['To'] = email
        msg.set_content(f"Hi {name},\n\nThis is a reminder for your follow-up scheduled on {follow_up_date}.\n\nBest Regards,\nYour Team")
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("your_email@gmail.com", "your_app_password")  # Replace with your credentials
            server.send_message(msg)
        st.success(f"Reminder sent to {name} at {email}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

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
    
    # Send email reminder
    send_email(name, email, follow_up_date)

# Display leads
st.subheader("Leads List")
if not leads_data.empty:
    st.dataframe(leads_data)
else:
    st.info("No leads yet. Add some leads to get started.")
