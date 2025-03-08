import streamlit as st
import requests

st.title("📩 AI-Powered Cold Email Generator")

# Upload Resume
uploaded_file = st.file_uploader("📤 Upload Your Resume (PDF Only)", type=["pdf"])

# Job Posting URL
job_url = st.text_input("🔗 Enter Job Posting URL")

if uploaded_file and job_url:
    st.success("✅ Resume Uploaded & Job URL Entered!")

    # Send resume to backend
    with st.spinner("Extracting resume details..."):
        response = requests.post(
            "https://cold-email-backend.vercel.app/upload-resume/",
            files={"file": uploaded_file.getvalue()}
        ).json()
        resume_data = response["data"]

    name = resume_data["Name"]
    skills = resume_data["Skills"]
    projects = resume_data["Projects"]

    st.subheader("👤 Extracted Resume Details:")
    st.write(f"**Name:** {name}")
    st.write(f"**Skills:** {skills}")
    st.write(f"**Projects:** {projects}")

    # Generate Cold Email
    with st.spinner("Generating Cold Email..."):
        email_response = requests.post(
            "https://cold-email-backend.vercel.app/generate-email/",
            data={"name": name, "job_url": job_url}
        ).json()

        cold_email = email_response["email"]

    st.subheader("✉️ Generated Cold Email:")
    st.write(cold_email)
else:
    st.warning("📥 Please upload a resume and enter a job URL to proceed.")
