# LearnBuddy

An AI-powered learning companion built with **Python Flask** and **IBM Watsonx.ai Granite Models**.  
LearnBuddy assesses your current skill level through a 5-question diagnostic quiz and then generates a personalised, modular course roadmap.

---

## Pages

| Page | Route | Description |
|---|---|---|
| **Track Selection** | `/` | Choose Frontend Development, Cyber Security, or UI/UX Design |
| **Diagnostic Quiz** | `/questionnaire/<track>` | 5 adaptive questions with animated step-by-step flow |
| **Course Roadmap** | `/roadmap` | AI-generated 5-module learning path with milestones, topics, resources, and per-module Granite AI tips |

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure credentials
```bash
cp .env.example .env
# Edit .env and fill in your IBM Watsonx.ai API key and Project ID
```

### 3. Run the app
```bash
python app.py
# Open http://localhost:5000
```

---

## IBM Watsonx.ai Setup

1. Sign in to [IBM Cloud](https://cloud.ibm.com) and provision a **Watsonx.ai** service.
2. Create a Project and note the **Project ID**.
3. Generate an **API Key** from *Manage → Access (IAM) → API Keys*.
4. Set values in your `.env` file:

```env
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=any_random_secret
```

> **No credentials?** The app works fully with rich built-in mock roadmaps — great for demos.

---

## Model Used

`ibm/granite-3-8b-instruct` — IBM's instruction-following Granite model via `ibm-watsonx-ai` SDK.

---

## Project Structure

```
LearnBuddy/
├── app.py               # Flask routes and Jinja2 filters
├── watsonx_client.py    # Watsonx.ai SDK wrapper + mock fallbacks
├── requirements.txt
├── .env.example
├── test_app.py          # Smoke tests (py -3 test_app.py)
└── templates/
    ├── base.html        # Shared layout, nav, footer
    ├── index.html       # Track selection landing page
    ├── questionnaire.html  # Animated 5-step diagnostic quiz
    └── roadmap.html     # Modular course roadmap with AI tips
```

---

## Running Tests

```bash
py -3 test_app.py
```
