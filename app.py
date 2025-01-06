import streamlit as st
from github import Github
from vertexai import controlflow as cf

# Streamlit UI for user inputs
st.title("GitHub Code Assistant")

# Input fields for GitHub token and repository details
github_token = st.text_input("Enter your GitHub Token", type="password")
repo_name = st.text_input("Enter the Repository Name (e.g., user/repo_name)")
file_path = st.text_input("Enter the File Path in the Repository")
user_question = st.text_area("What question do you have about the code in this file?")

# Button to trigger analysis
if st.button("Analyze Code"):
    if not github_token or not repo_name or not file_path or not user_question:
        st.error("Please fill in all fields.")
    else:
        # Fetch code from the GitHub repository
        def fetch_code_from_repo(file_path: str):
            g = Github(github_token)
            repo = g.get_repo(repo_name)
            try:
                file_content = repo.get_contents(file_path).decoded_content.decode("utf-8")
                return file_content
            except Exception as e:
                return f"Error fetching file: {e}"

        # Register the custom tool in ControlFlow
        cf.register_tool(fetch_code_from_repo)

        # Define the flow using ControlFlow
        @cf.flow
        def github_code_assistant():
            # Step 1: Fetch code content from the repository
            code_content = cf.run(
                f"Fetch the content of the file '{file_path}' from the GitHub repository.",
                tool="fetch_code_from_repo",
                params={"file_path": file_path}
            )

            # Step 2: Use an AI agent to analyze and answer the user's question based on the code
            ai_agent = cf.Agent(
                name="CodeAnalyzer",
                instructions="You are an expert software engineer. Analyze the provided code and answer questions about it."
            )
            answer = ai_agent.run(
                f"Based on this code, answer the user's question: {user_question}",
                context={"code": code_content}
            )

            return {
                "question": user_question,
                "file_path": file_path,
                "code_snippet": code_content,
                "answer": answer
            }

        # Run the flow and display results in Streamlit
        result = github_code_assistant()
        if isinstance(result, dict):
            st.subheader("Results")
            st.write(f"**Question:** {result['question']}")
            st.write(f"**File Path:** {result['file_path']}")
            st.code(result['code_snippet'], language="python")
            st.write(f"**Answer:** {result['answer']}")
        else:
            st.error("An error occurred during processing.")