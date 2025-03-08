import pandas as pd
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
import chromadb
import uuid

# 🔹 Initialize LangChain Model
llm = ChatGroq(
    temperature=0, 
    groq_api_key="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",  # 🔹 Add your API key
    model_name="llama-3.3-70b-versatile"
)

# 🔹 Scrape job description
def scrape_job_posting(url):
    """Fetch job details from the job URL."""
    loader = WebBaseLoader(url)
    page_data = loader.load().pop().page_content
    return page_data[:5000]  # Limit text for LLM processing

# 🔹 Store Resume Data in ChromaDB
client = chromadb.PersistentClient("vectorstore")
collection = client.get_or_create_collection(name="portfolio")

def store_resume_in_db(name, skills, projects):
    resume_id = str(uuid.uuid4())
    collection.add(
        documents=[skills],  
        metadatas={"name": name, "links": projects},
        ids=[resume_id]
    )

# 🔹 Retrieve Resume Details from ChromaDB
def get_resume_from_db():
    resume_data = collection.get(include=["documents", "metadatas"])
    if resume_data["documents"]:
        name = resume_data["metadatas"][0].get("name", "Unknown Candidate")
        skills = resume_data["documents"][0]
        projects = resume_data["metadatas"][0].get("links", "No Projects Found")
        return name, skills, projects
    return "Unknown Candidate", "No Skills Found", "No Projects Found"

# 🔹 Generate Cold Email
def generate_email(name, skills, job_desc, projects):
    prompt_email = PromptTemplate.from_template(
        """
        ### JOB DESCRIPTION:
        {job_description}
        
        ### INSTRUCTION:
        You are {candidate_name}, a highly skilled professional with expertise in {skills}. 
        You are applying for the above job. Your job is to write a **cold email** to the recruiter, highlighting how your experience 
        and skills align with their needs.
        
        Also, mention the most relevant projects from the following list to showcase your experience: {link_list}

        Do not provide a preamble. Keep the email **professional, concise, and personalized**.
        
        ### EMAIL (NO PREAMBLE):
        
        """
    )
    chain_email = prompt_email | llm  
    response = chain_email.invoke({
        "candidate_name": name,
        "skills": skills,
        "job_description": job_desc,
        "link_list": projects
    })
    return response.content
