from mcp.server.fastmcp import FastMCP
import os
import uuid
import numpy as np
import pandas as pd
import faiss
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

mcp = FastMCP("ColdMailGenerator")

load_dotenv() 
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

@mcp.tool()
def send_email(receiver_email:str, subject:str, body:str)->str:
    """
    Sends an email to the specified recipient.

    Args:
        receiver_email (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The main content/body of the email.

    Returns:
        str: A success message if the email is sent, or an error description.
    """
    sender_email = os.environ.get("MAIL_ID")
    sender_password = os.environ.get("PASSWORD")

    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message["Bcc"] = receiver_email 

        message.attach(MIMEText(body, "plain"))

      
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls() 
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return f"Email sent successfully to {receiver_email}!"

    except smtplib.SMTPAuthenticationError:
        
        return "Error: Could not authenticate. Please check your email credentials. If using Gmail with 2FA, you might need to generate an 'App Password'."
    except smtplib.SMTPConnectError as e:
       
        return f"Error: Could not connect to the SMTP server. Check internet or server details: {e}"
    except Exception as e:
       
        return f"An unexpected error occurred: {e}"

@mcp.tool()
def generate_cold_email(link: str) -> str:
    """
    Generates a cold email draft based on a job posting URL.

    Args:
        link (str): The URL of the job posting.

    Returns:
        str: The generated cold email content.
    """

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3, max_tokens=500)

    loader = WebBaseLoader(link)
    page_data = loader.load().pop().page_content

 
    prompt_extract = PromptTemplate.from_template(
        """
        ### SCRAPED TEXT FROM WEBSITE:
        {page_data}
        ### INSTRUCTION:
        Extract the job posting details and return them in JSON format with keys: `role`, `experience`, `skills` (list of strings), and `description`. Only return valid JSON.
        ### VALID JSON (NO PREAMBLE):
        """
    )
    chain_extract = prompt_extract | llm
    res = chain_extract.invoke(input={'page_data': page_data})

    json_parser = JsonOutputParser()
    parsed_json = json_parser.parse(res.content)

    if isinstance(parsed_json, list) and parsed_json:
        job = parsed_json[0]
    elif isinstance(parsed_json, dict):
        job = parsed_json
    else:
        
        job = {}
        print(f"Error: LLM output parsed to unexpected type: {type(parsed_json)}. Expected dict or list.")

    if not isinstance(job.get('skills'), list):
       
        if isinstance(job.get('skills'), str):
            job['skills'] = [skill.strip() for skill in job['skills'].split(',') if skill.strip()]
        else:
            job['skills'] = []
            print(f"Warning: 'skills' field is not a list or convertible string. Setting to empty list.")

    df = pd.read_csv("Path of excel file")
    vectors = embeddings.embed_documents(df["Techstack"].tolist())
    vectors = np.array(vectors)

    
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

 
    metadata = [{"links": row["Links"], "id": str(uuid.uuid4())} for _, row in df.iterrows()]


    if job.get('skills'):
        skill_vectors = embeddings.embed_documents(job['skills'])
        query_vector = np.mean(skill_vectors, axis=0) 
    else:
   
        print("No skills extracted for embedding. Using a zero vector for query.")
        query_vector = np.zeros(embeddings.embed_query("dummy").shape)

    k = 5
    distances, indices = index.search(np.array([query_vector]), k)
    relevant_links = [metadata[i]["links"] for i in indices[0]]


    prompt_email = PromptTemplate.from_template(
        """
        ### JOB DESCRIPTION:
        {job_description}

        ### INSTRUCTION:
        You are Nithesh Yetikuri, a Software Engineer at Cognizant, an AI & Software Consulting company that integrates business processes via automated tools.
        We empower enterprises with tailored solutions for scalability, optimization, cost reduction, and efficiency.
        Write a cold email to the client for the job above, highlighting Cognizant's capabilities.
        Include relevant portfolio links from: {link_list}
        Remember your identity: Nithesh Yetikuri, Software Engineer at Cognizant. Do not provide a preamble.
        ### EMAIL (NO PREAMBLE):
        """
    )
    chain_email = prompt_email | llm
    res = chain_email.invoke({"job_description": str(job), "link_list": relevant_links})

    return res.content

if __name__ == "__main__":
    mcp.run(transport="stdio")