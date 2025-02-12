# ColdMailGenerator
##Description
coldMailGenerator is a Streamlit-based application designed to streamline the process of creating personalized cold emails for potential clients. This tool helps you scrape job postings from various websites, analyze the extracted data, and generate tailored emails to showcase your team's expertise and past projects. Instead of hiring new employees, companies can leverage your team's skills and experience to meet their needs.

##Features
Scrape Job Postings: Easily extract job details from URLs of job postings.
Generate Personalized Emails: Automatically create tailored emails based on the scraped job data.
Showcase Your Expertise: Highlight your team's skills, experience, and successful projects to attract clients.
Streamline Client Outreach: Simplify the process of reaching out to potential clients with customized proposals.
How to Use
Enter the URL of the job posting you want to target.
Click the "Scrape" button to extract the job details.
Review the extracted data and customize the generated email if needed.
Send the personalized email to the potential client, showcasing how your team can fulfill their requirements.
##Installation
To install the required packages, run:

pip install -r requirements.txt

Usage
To run the app, use the following command:

streamlit run app.py

##Models Used
Embedding Model: GoogleGenerativeAIEmbeddings (model: models/embedding-001)
LLM Model: ChatGoogleGenerativeAI (model: gemini-1.5-flash)
