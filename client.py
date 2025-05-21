import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from mcp_use import MCPAgent, MCPClient
import os

load_dotenv()
async def run_memory_chat():
    """Cold Mail generator and sender."""

    config_file = "mcp.json" 
    print(f"Loading config from: {config_file}")
    try:
        client = MCPClient.from_config_file(config_file)
        print("MCPClient initialized.")
    except Exception as e:
        print(f"Error initializing MCPClient: {e}")
        return

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=os.environ.get("GOOGLE_API_KEY")) #ADD API KEY
    system_prompt = (
    """
    You are Nithesh Yetikuri, a Software Engineer at Cognizant. Help users with job application emails.

    **Tools:**
    - `ColdMailGenerator.generate_cold_email(link: str)`: Drafts emails from job links.
    - `ColdMailGenerator.send_email(receiver_email: str, subject: str, body: str)`: Sends emails.

    **Guidelines:**

    1.  **Generate Email:**
        -   Use `generate_cold_email` with a job link.
        -   **Show draft first.**
        -   Ask if changes are needed or if to send.
        -   If sending without recipient email: **Ask: "Please mention the recipient's email ID."**
        -   For changes: Advise specifying feedback or providing link again.

    2.  **Send Email:**
        -   Use `send_email` when user confirms sending with recipient email.
        -   **Auto-generate subject** from job/email content. **DO NOT ask user for subject.**
        -   **Signature (ALWAYS append to body):**
            "Regards,
            Nithesh Yetikuri
            Software Engineer
            Cognizant"
        -   Confirm sending or report errors.

    3.  **General:** Be professional, empathetic. Ask for missing info. Maintain context. Decline unsupported requests politely. No fabrication.
    """
    )

    # Create agent with memory_enabled=True
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True, 
        system_prompt=system_prompt
 
    )
    print("MCPAgent initialized.")

    print("\n===== Interactive MCP Chat =====")
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("==================================\n")

    try:

        while True:
            # Get user input
            user_input = input("\nYou: ")
            print(f"User input: {user_input}")

            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation...")
                break

            # Check for clear history command
            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Conversation history cleared.")
                continue

            # Get response from agent
            print("\nAssistant: ", end="", flush=True)

            try:
                print("Calling agent.run()")
                # Run the agent with the user input (memory handling is automatic)
                response = await agent.run(user_input)
                print("agent.run() returned.")
                print(response)

            except Exception as e:
                print(f"\nError in agent.run(): {e}")

    finally:
        # Clean up
        print("Entering finally block for cleanup.")
        if client and client.sessions:
            print("Closing client sessions.")
            await client.close_all_sessions()
            print("Client sessions closed.")
        print("Exiting finally block.")



if __name__ == "__main__":
    print("Calling asyncio.run(run_memory_chat())")
    asyncio.run(run_memory_chat())
    print("asyncio.run(run_memory_chat()) returned")
