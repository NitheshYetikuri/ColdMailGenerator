# AI-Powered Cold Email Generator

This project provides an AI-powered assistant that can generate and send personalized cold emails based on job postings. It leverages the Model Context Protocol (MCP) to allow a Large Language Model (LLM) to interact with custom tools for web scraping, email generation, and email sending.

-----

## Features

  * **Intelligent Cold Email Generation**: Provide a job posting URL, and the AI will extract relevant details (role, experience, skills, description) to draft a tailored cold email.
  * **Automated Subject Line Generation**: The AI automatically infers a suitable and professional subject line for the generated email based on the job posting and email content.
  * **Automated Email Sending**: After reviewing the generated email, you can instruct the AI to send it to a specified recipient.
  * **Custom Professional Signature**: All outgoing emails are automatically appended with a professional signature: "Regards, Nithesh Yetikuri, Software Engineer, Cognizant."
  * **Context-Aware Conversation**: The AI maintains conversation history, allowing for a natural and interactive experience where it understands follow-up commands and asks for necessary information (like the recipient's email ID).
  * **Scalable Architecture**: Built using MCP, enabling easy extension with more tools and functionalities.

-----

## How it Works

The project operates with two core components working in tandem:

1.  **`server.py` (MCP Server - `ColdMailGenerator`)**: This script acts as the backend, hosting specialized tools that the AI can call upon.

      * **`generate_cold_email`**: This tool is responsible for visiting a provided job posting URL, intelligently extracting key details from the webpage, and then using that information, along with a `techstack.csv` file (containing relevant portfolio links), to craft the initial cold email draft.
      * **`send_email`**: This tool handles the actual dispatch of the email. It connects to an SMTP server (like Gmail's) and sends the email with the specified recipient, subject, and body. It's configured to append your professional signature automatically.

2.  **`client.py` (MCP Client & AI Agent)**: This script serves as your interactive interface with the AI.

      * It uses a powerful Large Language Model (LLM), such as **Gemini 1.5 Pro**, to understand your natural language commands and questions.
      * A sophisticated **system prompt** guides the LLM's behavior. This prompt dictates how the AI should engage in conversation, when to invoke specific tools from the `ColdMailGenerator` server, what follow-up questions to ask (e.g., if a recipient email is missing), and how to ensure the email content (like the subject and signature) is correctly formatted.
      * The `client.py` connects to `server.py` using a configuration defined in `mcp.json`, which specifies how to launch and communicate with the `ColdMailGenerator` server.

This architecture allows the AI to perform complex, multi-step tasks like email generation and sending through simple, conversational commands, with the underlying logic handled by the specialized tools.

-----

## Usage

To use the AI-powered cold email generator, you need to run both the server and the client components.


1.  **Start the MCP Client:**
    Open a **separate** terminal, navigate to your project directory, and run the client script:

    ```bash
    uv run client.py
    ```