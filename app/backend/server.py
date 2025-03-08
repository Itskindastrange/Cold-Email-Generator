from fastapi import FastAPI, UploadFile, Form
import pdf_to_csv
import backend_email_gen

app = FastAPI()

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile):
    """API to process a PDF resume and return extracted details."""
    with open("uploaded_resume.pdf", "wb") as f:
        f.write(await file.read())

    details = pdf_to_csv.process_resume("uploaded_resume.pdf")
    return {"status": "success", "data": details}

@app.post("/generate-email/")
async def generate_email(name: str = Form(...), job_url: str = Form(...)):
    """API to generate a cold email."""
    job_desc = backend_email_gen.scrape_job_posting(job_url)
    skills, projects = backend_email_gen.get_resume_from_db()
    
    email = backend_email_gen.generate_email(name, skills, job_desc, projects)
    return {"status": "success", "email": email}

@app.get("/")
def home():
    return {"message": "Backend is running!"}
