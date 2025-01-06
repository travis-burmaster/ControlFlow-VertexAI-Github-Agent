import streamlit as st
from github import Github
from vertexai import controlflow as cf
from controlflow import Flow
from controlflow.tools import Tool, ToolInput, ToolOutput

# Streamlit UI for user inputs
st.title("GitHub Code Assistant")

# Input fields for GitHub token and repository details
github_token = st.text_input("Enter your GitHub Token", type="password")
repo_name = st.text_input("Enter the Repository Name (e.g., user/repo_name)")
file_path = st.text_input("Enter the File Path in the Repository")
user_question = st.text_area("What question do you have about the code in this file?")

# Define the GitHub code fetching tool
class GitHubCodeFetcher(Tool):
    name = "github_code_fetcher"
    description = "Fetches code content from a GitHub repository"
    inputs = {"file_path": ToolInput(description="Path to the file in the repository")}
    outputs = {"code": ToolOutput(description="Content of the file")}

    def execute(self, inputs):
        try:
            g = Github(github_token)
            repo = g.get_repo(repo_name)
            file_content = repo.get_contents(inputs["file_path"]).decoded_content.decode("utf-8")
            return {"code": file_content}
        except Exception as e:
            return {"code": f"Error fetching file: {e}"}

# Button to trigger analysis
if st.button("Analyze Code"):
    if not github_token or not repo_name or not file_path or not user_question:
        st.error("Please fill in all fields.")
    else:
        # Create the flow
        flow = Flow()
        
        # Register the GitHub code fetching tool
        flow.register_tool(GitHubCodeFetcher())

        # Define the analysis steps
        @flow.task
        async def fetch_code(context):
            result = await context.run_tool(
                "github_code_fetcher",
                {"file_path": file_path}
            )
            return result["code"]

        @flow.task
        async def analyze_code(context, code_content):
            result = await context.run_agent(
                role="You are an expert software engineer. Analyze the provided code and answer questions about it.",
                task=f"Based on this code, answer the user's question: {user_question}",
                inputs={"code": code_content}
            )
            return result

        # Define the main workflow
        @flow.workflow
        async def github_code_assistant(context):
            code_content = await fetch_code(context)
            answer = await analyze_code(context, code_content)
            
            return {
                "question": user_question,
                "file_path": file_path,
                "code_snippet": code_content,
                "answer": answer
            }

        try:
            # Run the flow
            result = flow.run(github_code_assistant)

            # Display results in Streamlit
            if isinstance(result, dict):
                st.subheader("Results")
                st.write(f"**Question:** {result['question']}")
                st.write(f"**File Path:** {result['file_path']}")
                st.code(result['code_snippet'], language="python")
                st.write(f"**Answer:** {result['answer']}")
            else:
                st.error("An error occurred during processing.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
