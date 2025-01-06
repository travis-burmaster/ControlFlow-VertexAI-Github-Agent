# ControlFlow-VertexAI-Github-Agent

A Streamlit application that leverages Vertex AI's ControlFlow to analyze GitHub repository code and answer questions about it using AI.

## Features

- Connect to GitHub repositories using personal access tokens
- Fetch and analyze code from specific files in repositories
- Use Vertex AI's ControlFlow to process and analyze code
- Get AI-powered answers to questions about your code
- User-friendly Streamlit interface

## Prerequisites

- Python 3.7+
- GitHub Account and Personal Access Token
- Google Cloud Project with Vertex AI enabled
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/travis-burmaster/ControlFlow-VertexAI-Github-Agent.git
cd ControlFlow-VertexAI-Github-Agent
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. In the web interface:
   - Enter your GitHub personal access token
   - Provide the repository name (format: user/repo_name)
   - Enter the file path you want to analyze
   - Ask your question about the code
   - Click 'Analyze Code' to get AI-powered insights

## How It Works

1. The application uses the GitHub API to fetch code from specified repositories
2. Vertex AI's ControlFlow orchestrates the analysis process:
   - Fetches code content using custom tools
   - Utilizes an AI agent to analyze the code
   - Generates comprehensive answers to user questions
3. Results are displayed in a user-friendly format via Streamlit

## Security Note

- Never commit your GitHub token or other sensitive credentials
- Use environment variables for sensitive information in production
- Ensure appropriate repository permissions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.