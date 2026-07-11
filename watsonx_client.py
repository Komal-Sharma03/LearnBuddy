"""
IBM Watsonx.ai client — uses ibm-watsonx-ai SDK with granite-3-8b-instruct.
Falls back to a structured mock when credentials are not configured.
"""
import os
import json
import re

try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False

# ── helpers ──────────────────────────────────────────────────────────────────

def _get_model():
    api_key = os.getenv("WATSONX_API_KEY", "")
    project_id = os.getenv("WATSONX_PROJECT_ID", "")
    url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    if not _SDK_AVAILABLE or not api_key or api_key.startswith("your_"):
        return None

    try:
        credentials = Credentials(url=url, api_key=api_key)
        model = ModelInference(
            model_id="ibm/granite-3-8b-instruct",
            credentials=credentials,
            project_id=project_id,
            params={
                GenParams.MAX_NEW_TOKENS: 900,
                GenParams.TEMPERATURE: 0.4,
                GenParams.REPETITION_PENALTY: 1.1,
            },
        )
        return model
    except Exception as exc:
        print(f"[Watsonx] Could not initialise model (will use mock): {exc}")
        return None


def _call_watsonx(prompt: str) -> str:
    model = _get_model()
    if model is None:
        return ""
    try:
        response = model.generate_text(prompt=prompt)
        return response.strip()
    except Exception as exc:
        print(f"[Watsonx] Error: {exc}")
        return ""


# ── roadmap generation ────────────────────────────────────────────────────────

_ROADMAP_PROMPT = """<|system|>
You are LearnBuddy, an expert learning coach. Given a learner's skill assessment, generate a structured, personalised course roadmap in valid JSON only — no markdown, no extra text.

Output format (strictly JSON):
{{
  "level": "<Beginner|Intermediate|Advanced>",
  "summary": "<2-sentence personalised summary>",
  "modules": [
    {{
      "order": 1,
      "title": "<module title>",
      "duration": "<e.g. 2 weeks>",
      "topics": ["topic1", "topic2", "topic3"],
      "resources": ["resource1", "resource2"],
      "milestone": "<what learner can do after this module>"
    }}
  ]
}}
Generate 5 modules appropriate for the learner's level. Keep it concise and actionable.
<|user|>
Track: {track}
Learner Assessment:
{skill_summary}
<|assistant|>
"""

_MOCK_ROADMAPS = {
    "Frontend Development": {
        "level": "Beginner",
        "summary": "You are starting your frontend journey with little prior experience. This roadmap takes you from HTML basics all the way to building interactive React applications.",
        "modules": [
            {"order": 1, "title": "HTML & CSS Foundations", "duration": "2 weeks", "topics": ["Semantic HTML5", "CSS Box Model", "Flexbox & Grid", "Responsive Design"], "resources": ["MDN Web Docs", "freeCodeCamp HTML/CSS"], "milestone": "Build a fully responsive personal webpage"},
            {"order": 2, "title": "JavaScript Essentials", "duration": "3 weeks", "topics": ["Variables & Data Types", "Functions & Scope", "DOM Manipulation", "Events & Listeners"], "resources": ["javascript.info", "Eloquent JavaScript"], "milestone": "Create an interactive to-do list app"},
            {"order": 3, "title": "Modern JavaScript (ES6+)", "duration": "2 weeks", "topics": ["Arrow Functions", "Promises & Async/Await", "Modules & Imports", "Array Methods"], "resources": ["ES6 for Everyone (Wes Bos)", "MDN ES6 Guide"], "milestone": "Fetch and display data from a public API"},
            {"order": 4, "title": "React Fundamentals", "duration": "4 weeks", "topics": ["Components & Props", "State & Hooks", "React Router", "Form Handling"], "resources": ["React Official Docs", "Scrimba React Course"], "milestone": "Build a multi-page React SPA"},
            {"order": 5, "title": "Version Control & Deployment", "duration": "1 week", "topics": ["Git & GitHub", "Branching Strategy", "Netlify/Vercel Deployment", "CI/CD Basics"], "resources": ["Pro Git Book", "GitHub Learning Lab"], "milestone": "Deploy your React app to production"},
        ],
    },
    "Cyber Security": {
        "level": "Beginner",
        "summary": "Your assessment shows foundational curiosity about security. This roadmap builds core networking knowledge and gradually introduces offensive and defensive security techniques.",
        "modules": [
            {"order": 1, "title": "Networking Fundamentals", "duration": "2 weeks", "topics": ["OSI Model", "TCP/IP Suite", "DNS & HTTP", "Subnetting Basics"], "resources": ["CompTIA Network+ Study Guide", "Professor Messer's N+"], "milestone": "Explain how a web request travels end-to-end"},
            {"order": 2, "title": "Linux & Command Line", "duration": "2 weeks", "topics": ["File System Navigation", "User & Permission Management", "Bash Scripting", "Process Monitoring"], "resources": ["OverTheWire: Bandit", "Linux Journey"], "milestone": "Automate a system admin task with a Bash script"},
            {"order": 3, "title": "Security Fundamentals", "duration": "3 weeks", "topics": ["CIA Triad", "Common Vulnerabilities (OWASP Top 10)", "Cryptography Basics", "Firewalls & IDS"], "resources": ["TryHackMe Pre-Security Path", "CompTIA Security+"], "milestone": "Identify vulnerabilities in a demo web app"},
            {"order": 4, "title": "Ethical Hacking Tools", "duration": "3 weeks", "topics": ["Nmap Scanning", "Wireshark Analysis", "Metasploit Framework", "Burp Suite Basics"], "resources": ["Hack The Box Starting Point", "TryHackMe Jr Penetration Tester"], "milestone": "Complete 3 beginner Hack The Box machines"},
            {"order": 5, "title": "CTF Challenges & Report Writing", "duration": "2 weeks", "topics": ["Web Exploitation", "Reverse Engineering Basics", "Steganography", "Penetration Test Report"], "resources": ["PicoCTF", "CTFtime.org"], "milestone": "Complete a beginner CTF and write a findings report"},
        ],
    },
    "UI/UX Design": {
        "level": "Beginner",
        "summary": "You are new to UI/UX design. This roadmap introduces design thinking principles and equips you with Figma skills to produce professional-grade prototypes.",
        "modules": [
            {"order": 1, "title": "Design Thinking & UX Basics", "duration": "1 week", "topics": ["Empathize, Define, Ideate", "User Personas", "User Journey Maps", "Problem Statements"], "resources": ["IDEO Design Thinking", "Nielsen Norman Group Articles"], "milestone": "Create a user persona and journey map for a product idea"},
            {"order": 2, "title": "Visual Design Principles", "duration": "2 weeks", "topics": ["Typography Hierarchy", "Color Theory", "Spacing & Layout", "Gestalt Principles"], "resources": ["Refactoring UI Book", "Canva Design School"], "milestone": "Redesign an existing app screen with improved visuals"},
            {"order": 3, "title": "Figma Fundamentals", "duration": "3 weeks", "topics": ["Frames & Components", "Auto Layout", "Styles & Variables", "Prototyping & Interactions"], "resources": ["Figma YouTube Tutorials", "Figma Community Files"], "milestone": "Design a complete mobile app in Figma with 5+ screens"},
            {"order": 4, "title": "UX Research Methods", "duration": "2 weeks", "topics": ["User Interviews", "Usability Testing", "Card Sorting", "Affinity Diagramming"], "resources": ["UX Research Cheat Sheet (NN/g)", "Maze.co Tutorials"], "milestone": "Conduct 3 usability tests and synthesize findings"},
            {"order": 5, "title": "Accessibility & Portfolio", "duration": "2 weeks", "topics": ["WCAG 2.1 AA Standards", "Color Contrast", "Screen Reader Design", "Case Study Writing"], "resources": ["WebAIM", "UX Portfolio Bootcamp (CareerFoundry)"], "milestone": "Publish a portfolio case study with before/after designs"},
        ],
    },
}


def generate_roadmap(track_label: str, skill_summary: str) -> dict:
    prompt = _ROADMAP_PROMPT.format(track=track_label, skill_summary=skill_summary)
    raw = _call_watsonx(prompt)

    if raw:
        # extract the first JSON object from the response
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

    # Fallback: detect level from answers and return mock
    mock = _MOCK_ROADMAPS.get(track_label, list(_MOCK_ROADMAPS.values())[0])
    return mock


def generate_question(track: str, topic: str) -> str:
    prompt = (
        f"<|system|>You are LearnBuddy, a concise learning coach. Give a 2-3 sentence practical tip "
        f"for someone learning about '{topic}' in {track}. Be direct and actionable.\n"
        f"<|user|>Give me a quick tip for: {topic}\n<|assistant|>"
    )
    result = _call_watsonx(prompt)
    if result:
        return result

    tips = {
        "default": f"Focus on hands-on practice with {topic}. Build small projects to reinforce concepts and refer to official documentation often."
    }
    return tips.get(topic.lower(), tips["default"])
