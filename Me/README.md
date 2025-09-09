---
title: Me
app_file: Me.py
sdk: gradio
sdk_version: 5.42.0
---
## Me Agent

A simple personal website chat agent that answers questions about me using my profile (summary text + LinkedIn PDF) and can optionally send push notifications when a user shares contact details or asks something the agent cannot answer.

sample demo: https://huggingface.co/spaces/Drew88/Me

### Features
- Answers questions using your provided summary and LinkedIn PDF content
- Launches a Gradio chat UI locally
- Records contact details via a tool call and sends a Pushover notification
- Records unknown questions via a tool call and sends a Pushover notification

### Requirements
- Python 3.10+
- Dependencies from the repository root `requirements.txt`
- OpenAI API access
- Optional: Pushover account for notifications

### Setup
1. Create and activate a virtual environment (recommended)
```bash
python -m venv .venv
# Windows PowerShell
. .venv\\Scripts\\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

2. Install dependencies from the repository root
```bash
pip install -r requirements.txt
```

3. Create a `.env` file at the repository root (same folder as `requirements.txt`)
```env
OPENAI_API_KEY=your_openai_api_key
# Optional (only if you want push notifications via Pushover)
PUSHOVER_USER=your_pushover_user_key
PUSHOVER_TOKEN=your_pushover_app_token
```

4. Place your profile files in this folder `python_agents/Me/`
- `summary.txt` — a short bio/summary of your background
- `linkedin.pdf` — export of your LinkedIn profile

The code will read these two files from `python_agents/Me/summary.txt` and `python_agents/Me/linkedin.pdf`.

### Run
From the repository root or from `python_agents/Me/`, run:
```bash
python python_agents/Me/Me.py
```

This will launch a Gradio interface and output a local URL (typically `http://127.0.0.1:7860`). Open it in your browser to chat.

### How it works (high level)
- Loads environment variables via `python-dotenv`
- Reads `summary.txt` and OCR-extracts text from `linkedin.pdf` using `pypdf`
- Builds a system prompt representing you and your background
- Starts a chat loop with the OpenAI API using the `gpt-4o-mini` model
- Exposes two function tools:
  - `record_user_details(email, name?, notes?)`
  - `record_unknown_question(question)`
  Both send notifications via Pushover if configured

### Customization
- Change the displayed name by editing `name` in `Me.py`
- Update the model in `Me.py` if desired
- Adjust the system prompt to better match your tone and goals

### Troubleshooting
- If `linkedin.pdf` or `summary.txt` is missing, the app will still run but may warn and have less context
- If you don't use Pushover, leave those variables unset; the app will skip notifications
- Ensure `OPENAI_API_KEY` is set in `.env` and the virtual environment is activated

### Security notes
- Do not commit your `.env` with secrets
- Treat `summary.txt` and `linkedin.pdf` as personal data



