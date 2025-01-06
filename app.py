import os
from typing import Dict, Any

import streamlit as st
from github import Github
from dotenv import load_dotenv
from controlflow import Flow, Task
import controlflow as cf
from controlflow.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Constants for API keys
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Set default model for ControlFlow
cf.defaults.model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-002", temperature=0.2)

# Streamlit UI for user inputs
st.title("GitHub Repository Code Assistant")

# Input fields for GitHub token and repository details
github_token = st.text_input("Enter your GitHub Token", type="password", value=GITHUB_TOKEN)
repo_name = st.text_input("Enter the Repository Name (e.g., user/repo_name)")
user_question = st.text_area("What question do you have about the code in this repository?")

def fetch_repo_content(github_token: str, repo_name: str) -> Dict[str, Any]:
    """Fetches the content of a GitHub repository."""
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        tree = repo.get_git_tree(sha="main", recursive=True).tree

        repo_content = {}
        for item in tree:
            if item.type == "blob":
                file_content = repo.get_contents(item.path).decoded_content.decode("utf-8")
                repo_content[item.path] = file_content

        return {"repo_content": repo_content}
    except Exception as e:
        return {"error": f"Error fetching repository: {e}"}

async def analyze_repo_task(context, github_token: str, repo_name: str, user_question: str) -> Dict[str, Any]:
    """Task to analyze a repository and answer a user's question."""
    # Fetch repository content
    fetch_result = fetch_repo_content(github_token, repo_name)
    if "error" in fetch_result:
        return {"error": fetch_result["error"]}
    
    repo_content = fetch_result["repo_content"]

    # Analyze with agent
    result = await context.run_agent(
        role="You are an expert software engineer. Analyze the provided codebase and answer questions about it.",
        task=f"Based on this codebase, answer the user's question: {user_question}",
        inputs={"codebase": repo_content}
    )

    return {
        "question": user_question,
        "repo_files": list(repo_content.keys()),
        "answer": result
    }

def display_results(result: Dict[str, Any]):
    """Displays the results of the analysis in Streamlit."""
    if "error" in result:
        st.error(result["error"])
    else:
        st.subheader("Results")
        st.write(f"**Question:** {result['question']}")
        st.write(f"**Repository Files:**")
        for file_path in result['repo_files']:
            st.write(f"- {file_path}")
        st.write(f"**Answer:** {result['answer']}")

# Button to trigger analysis
if st.button("Analyze Repository"):
    if not github_token or not repo_name or not user_question:
        st.error("Please fill in all fields.")
    else:
        # Create the flow and define the analysis task
        flow = Flow()
        
        analyze_repo = cf.Task(
            name="Analyze Repository",
            func=lambda context: analyze_repo_task(context, github_token, repo_name, user_question)
        )

        try:
            # Run the flow with the defined task
            result = flow.run(analyze_repo)
            display_results(result)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
