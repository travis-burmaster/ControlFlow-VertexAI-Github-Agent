import streamlit as st
from github import Github
from controlflow import Flow
from controlflow.tools import Tool
import controlflow as cf
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

cf.defaults.model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-002", temperature=0.2)

# Streamlit UI for user inputs
st.title("GitHub Repository Code Assistant")

# Input fields for GitHub token and repository details
github_token = st.text_input("Enter your GitHub Token", type="password")
repo_name = st.text_input("Enter the Repository Name (e.g., user/repo_name)")
user_question = st.text_area("What question do you have about the code in this repository?")

# Define the GitHub repository fetching tool
class GitHubRepoFetcher(Tool):
    name = "github_repo_fetcher"
    description = "Fetches all code content from a GitHub repository"
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        try:
            g = Github(github_token)
            repo = g.get_repo(repo_name)
            tree = repo.get_git_tree(sha="main", recursive=True).tree  # Fetch all files recursively
            
            repo_content = {}
            for item in tree:
                if item.type == "blob":  # Only fetch files (not directories)
                    file_content = repo.get_contents(item.path).decoded_content.decode("utf-8")
                    repo_content[item.path] = file_content
            
            return {"repo_content": repo_content}
        except Exception as e:
            return {"repo_content": f"Error fetching repository: {e}"}

# Button to trigger analysis
if st.button("Analyze Repository"):
    if not github_token or not repo_name or not user_question:
        st.error("Please fill in all fields.")
    else:
        # Create the flow
        flow = Flow()
        
        # Register the GitHub repository fetching tool
        flow.register_tool(GitHubRepoFetcher())

        # Define the analysis steps
        @flow.task
        async def fetch_repo(context):
            result = await context.run_tool("github_repo_fetcher", {})
            return result["repo_content"]

        @flow.task
        async def analyze_repo(context, repo_content):
            result = await context.run_agent(
                role="You are an expert software engineer. Analyze the provided codebase and answer questions about it.",
                task=f"Based on this codebase, answer the user's question: {user_question}",
                inputs={"codebase": repo_content}
            )
            return result

        # Define the main workflow
        @flow.workflow
        async def github_repo_assistant(context):
            repo_content = await fetch_repo(context)
            answer = await analyze_repo(context, repo_content)
            
            return {
                "question": user_question,
                "repo_files": list(repo_content.keys()),
                "answer": answer
            }

        try:
            # Run the flow
            result = flow.run(github_repo_assistant)

            # Display results in Streamlit
            if isinstance(result, dict):
                st.subheader("Results")
                st.write(f"**Question:** {result['question']}")
                st.write(f"**Repository Files:**")
                for file_path in result['repo_files']:
                    st.write(f"- {file_path}")
                st.write(f"**Answer:** {result['answer']}")
            else:
                st.error("An error occurred during processing.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
