import pdfplumber
import pandas as pd
import json
from langchain_groq import ChatGroq

# 🔹 Initialize LangChain Model (Replace with your actual API key)
llm = ChatGroq(
    temperature=0, 
    groq_api_key="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",  # 🔹 Add your API key
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
        response_text = response.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(response_text)  # 🔹 Convert to JSON
    except Exception as e:
        print("❌ Error:", str(e))
        return {}

def process_resume(pdf_path, csv_output="resume_details.csv"):
    """Extract resume details and save to CSV."""
    text = extract_text_from_pdf(pdf_path)
    parsed_data = analyze_resume_with_groq(text)

    if parsed_data:
        details = {
            "Name": parsed_data.get("name", "Not Found"),
            "Email": parsed_data.get("email", "Not Found"),
            "Phone": parsed_data.get("phone", "Not Found"),
            "Skills": ", ".join(parsed_data.get("skills", [])) if parsed_data.get("skills") else "Not Found",
            "Experience": parsed_data.get("experience", "Not Found"),
            "Education": parsed_data.get("education", "Not Found"),
            "Projects": parsed_data.get("projects", "Not Found")
        }
        df = pd.DataFrame([details])
        df.to_csv(csv_output, index=False)
        return details  # 🔹 Return extracted details
    return None
