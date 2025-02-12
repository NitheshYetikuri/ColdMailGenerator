from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from langchain_community.document_loaders import WebBaseLoader
import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import JsonOutputParser
import pandas as pd
import uuid
import numpy as np
import faiss
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

st.title("Cold Mail generator AI")

st.write("""
Welcome to the Client Outreach and Project Proposal Generator! This app is designed to help you create personalized cold emails to potential clients, showcasing your team's expertise and past projects. Instead of hiring new employees, companies can leverage your team's skills and experience to meet their needs.
""")


embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


google_api_key = os.environ.get("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, max_tokens=500)
link=st.text_input("Enter the link here")
user_input = "https://careers.nike.com/lead-software-engineer/job/R-48873"
if(link):
    loader = WebBaseLoader(link)
    page_data = loader.load().pop().page_content

    prompt_extract = PromptTemplate.from_template(
        """
        ### SCRAPED TEXT FROM WEBSITE:
        {page_data}
        ### INSTRUCTION:
        The scraped text is from the career's page of a website.
        Your job is to extract the job postings and return them in JSON format containing the
        following keys: `role`, `experience`, `skills` and `description`.
        Only return the valid JSON.
        ### VALID JSON (NO PREAMBLE):
        """
    )

    chain_extract = prompt_extract | llm
    res = chain_extract.invoke(input={'page_data': page_data})


    json_parser = JsonOutputParser()
    json_res = json_parser.parse(res.content)
    job = json_res

    # Load your data
    df = pd.read_csv("techstack.csv")

    # Convert your documents to vectors
    vectors = embeddings.embed_documents(df["Techstack"].tolist())

    # Convert the list of vectors to a NumPy array
    vectors = np.array(vectors)

    # Create a FAISS index
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)

    # Add vectors to the index
    index.add(vectors)

    # Save metadata
    metadata = [{"links": row["Links"], "id": str(uuid.uuid4())} for _, row in df.iterrows()]
    # Example of searching the index
    query_vector = embeddings.embed_documents(job['skills'])[0]
    k = 5  # Number of nearest neighbors
    distances, indices = index.search(np.array([query_vector]), k)

    # Retrieve results
    results = [metadata[i] for i in indices[0]]

    prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            You are Nithesh Yetikuri, a Jr Software Engineer at Cognizant. Cognizant is an AI & Software Consulting company dedicated to facilitating
            the seamless integration of business processes through automated tools.
            we will see company career portals mention that as saw the advertisement
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability,
            process optimization, cost reduction, and heightened overall efficiency.
            Your job is to write a cold email to the client regarding the job mentioned above describing the capability of Cognizant
            in fulfilling their needs.
            Also add the most relevant ones from the following links to showcase Cognizant's portfolio: {link_list}
            Remember you are Nithesh Yetikuri, Jr Software Engineer at Cognizant.
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):

            """
            )

    chain_email = prompt_email | llm
    res = chain_email.invoke({"job_description": str(job), "link_list": results})
    st.text(res.content)