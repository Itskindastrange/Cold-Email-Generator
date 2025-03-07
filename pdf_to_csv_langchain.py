import pdfplumber
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from langchain_groq import ChatGroq
import os
import json

# 🔹 Load API Key from Environment Variable
#GROQ_CLOUD_API_KEY = os.getenv("GROQ_API_KEY")

# 🔹 Initialize LangChain Groq Model
llm = ChatGroq(
    temperature=0, 
    groq_api_key="",     #your API key
    model_name="llama-3.3-70b-versatile"
)

def extract_text_from_pdf(pdf_path):
    """Extract text from all pages of a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    print("\n✅ Extracted Resume Text:\n", text[:500], "\n... [Truncated for Debugging] ...\n")
    return text.strip()

def analyze_resume_with_groq(text):
    """Send the extracted text to Groq Cloud using LangChain."""
    prompt = f"""
    Extract the following details from the resume:
    - Name
    - Email
    - Phone Number
    - Skills (list them)
    - Experience (include job roles, company names, and duration)
    - Education (degree, university, years)
    - Projects (list project titles with descriptions)

    Resume Content:
    {text}

    Format the response in JSON with keys: name, email, phone, skills, experience, education, projects.
    """

    try:
        response = llm.invoke(prompt)  
        response_text = response.content  

        # 🔹 Remove the Markdown JSON formatting ("```json ... ```")
        response_text = response_text.strip().replace("```json", "").replace("```", "").strip()

        print("\n✅ Groq Cloud Response (Cleaned):\n", response_text)  

        parsed_data = json.loads(response_text)  
        return parsed_data

    except Exception as e:
        print("\n❌ Error with Groq Cloud API:", str(e))
        return {}

def format_experience(experience_list):
    """Converts experience list to a readable string."""
    if isinstance(experience_list, list):
        return "\n".join([
            f"{exp.get('role', 'Unknown Role')} at {exp.get('company', 'Unknown Company')} ({exp.get('duration', 'Unknown Duration')})"
            for exp in experience_list
        ])
    return "Not Found"

def format_education(education_list):
    """Converts education list to a readable string."""
    if isinstance(education_list, list):
        return "\n".join([
            f"{edu.get('degree', 'Unknown Degree')} from {edu.get('university', 'Unknown University')} ({edu.get('years', 'Unknown Duration')})"
            for edu in education_list
        ])
    return "Not Found"

def format_projects(project_list):
    """Converts project list to a readable string."""
    if isinstance(project_list, list):
        return "\n".join([
            f"{proj.get('title', 'Unknown Project')} - {proj.get('description', 'No description available')}"
            for proj in project_list
        ])
    return "Not Found"

def select_pdf_and_process():
    """Open file dialog to select a PDF resume and process it."""
    root = tk.Tk()
    root.withdraw()  

    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])

    if file_path:
        print(f"\n📄 Processing: {file_path}")
        text = extract_text_from_pdf(file_path)
        parsed_data = analyze_resume_with_groq(text)

        if parsed_data:
            details = {
                "Name": parsed_data.get("name", "Not Found"),
                "Email": parsed_data.get("email", "Not Found"),
                "Phone": parsed_data.get("phone", "Not Found"),
                "Skills": ", ".join(parsed_data.get("skills", [])) if parsed_data.get("skills") else "Not Found",
                "Experience": format_experience(parsed_data.get("experience", "Not Found")),  # ✅ Formatted experience
                "Education": format_education(parsed_data.get("education", "Not Found")),  # ✅ Formatted education
                "Projects": format_projects(parsed_data.get("projects", "Not Found"))  # ✅ Formatted projects
            }

            # Save to CSV
            df = pd.DataFrame([details])
            output_csv = "resume_details.csv"
            df.to_csv(output_csv, index=False)
            print(f"\n✅ Resume details saved to {output_csv}")
        else:
            print("\n❌ Failed to parse resume with Groq Cloud.")

# Run the function to open file dialog and process resume
select_pdf_and_process()
