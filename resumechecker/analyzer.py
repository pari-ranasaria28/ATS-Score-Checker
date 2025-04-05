import pdfplumber
import spacy
from groq import Groq
import json

def extract_text_from_pdf(pdf_path):
    text=""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = text + page.extract_text() + "\n"
    return text.strip()

# path="Pari_Ranasaria_Resume.pdf"
# extract_text_from_pdf(path)

API_KEY = "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"

def analyze_resume_with_llm(resume_text:str, job_description:str)->dict:
    prompt = f"""
        You are an AI assistant that analyses resumes for a software engineering job application. Given a name and a job description, extract the following details:
        1. Identify all skills mentioned in the resume.
        2. Calculate the total years of experience
        3. Categories the projects based on the domain(e.g. AI Webdevelopment, Cloud, etc.)
        4. Rank the resume relevance to the job description on a scale of 0 to 100.

        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Provide the output in valid JSON format with this structure:
        {{
            "rank":"<percentage>",
            "skills":["skill","skill2",....],
            "total_experience" : "<number of years>",
            "project_category" : ["category1","category2",....]
        }}
    """
    try:
        client = Groq(api_key = API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages = [{'role':'user','content':prompt}],
            temperature = 0.7,
            response_format = {'type':'json_object'}
        )
        result = response.choices[0].message.content
        return json.loads(result)
    
    except Exception as e:
        print(e)

def process_resume(pdf_path,job_description):
    try:
        resume_text = extract_text_from_pdf(pdf_path)
        data = analyze_resume_with_llm(resume_text,job_description)
        return data
    except Exception as e:
        print(e)
        return None
