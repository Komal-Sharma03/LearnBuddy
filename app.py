import os
import re
import json
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from watsonx_client import generate_roadmap, generate_question


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "learnbuddy-secret-2024")

# ── custom Jinja2 filters ──────────────────────────────────────────────────────
@app.template_filter("extract_weeks")
def extract_weeks(duration_str: str) -> int:
    """Pull the first integer from a duration string like '2 weeks'."""
    match = re.search(r"\d+", str(duration_str))
    return int(match.group()) if match else 1

# ── Diagnostic question bank per track ─────────────────────────────────────────
TRACKS = {
    "frontend": {
        "label": "Frontend Development",
        "icon": "🖥️",
        "color": "#3b82d4",
        "questions": [
            {"id": "q1", "text": "How comfortable are you with HTML & CSS?",
             "options": ["Never touched them", "I know the basics", "I build layouts confidently", "I can do advanced responsive design"]},
            {"id": "q2", "text": "What is your JavaScript experience?",
             "options": ["I haven't used JS", "I know variables and loops", "I work with DOM & events", "I use modern ES6+ and frameworks"]},
            {"id": "q3", "text": "Have you used any frontend framework?",
             "options": ["No frameworks yet", "I've tried React/Vue/Angular", "I build apps with a framework", "I architect large-scale SPAs"]},
            {"id": "q4", "text": "How do you handle version control (Git)?",
             "options": ["Never used Git", "I commit and push", "I branch, merge, and resolve conflicts", "I manage CI/CD pipelines"]},
            {"id": "q5", "text": "How familiar are you with web performance optimization?",
             "options": ["Not familiar", "I know lazy loading exists", "I profile and optimize bundles", "I implement advanced caching strategies"]},
        ],
    },
    "cybersecurity": {
        "label": "Cyber Security",
        "icon": "🔐",
        "color": "#7c5cd8",
        "questions": [
            {"id": "q1", "text": "What is your understanding of networking fundamentals?",
             "options": ["Very limited", "I know TCP/IP basics", "I understand routing and firewalls", "I design secure network architectures"]},
            {"id": "q2", "text": "How familiar are you with common attack vectors (e.g., SQL injection, XSS)?",
             "options": ["Never heard of them", "I've read about them", "I can identify and explain them", "I can exploit and mitigate them"]},
            {"id": "q3", "text": "Have you used any security tools (Wireshark, Nmap, Burp Suite)?",
             "options": ["No tools used", "I've installed one", "I use them regularly", "I build custom scripts around them"]},
            {"id": "q4", "text": "What is your experience with cryptography?",
             "options": ["No experience", "I know hashing vs. encryption", "I implement TLS/PKI solutions", "I design cryptographic systems"]},
            {"id": "q5", "text": "Have you participated in CTF challenges or security audits?",
             "options": ["Never", "Tried a beginner CTF", "Regular CTF participant", "I lead red-team engagements"]},
        ],
    },
    "uiux": {
        "label": "UI/UX Design",
        "icon": "🎨",
        "color": "#e05c3a",
        "questions": [
            {"id": "q1", "text": "How experienced are you with design tools (Figma, Adobe XD)?",
             "options": ["Never used any", "I've opened Figma once", "I design screens and prototypes", "I manage design systems at scale"]},
            {"id": "q2", "text": "What is your understanding of UX research methods?",
             "options": ["Not familiar", "I know surveys exist", "I conduct user interviews and usability tests", "I lead mixed-method research programs"]},
            {"id": "q3", "text": "How well do you understand typography and color theory?",
             "options": ["No knowledge", "Basic awareness", "I apply principles consistently", "I create brand guidelines"]},
            {"id": "q4", "text": "Have you created interactive prototypes?",
             "options": ["Never", "Static mockups only", "Click-through prototypes", "High-fidelity animated prototypes"]},
            {"id": "q5", "text": "How familiar are you with accessibility (WCAG) standards?",
             "options": ["Not familiar", "I've heard of WCAG", "I apply AA guidelines", "I audit and remediate for full compliance"]},
        ],
    },
}


@app.route("/")
def index():
    session.clear()
    return render_template("index.html", tracks=TRACKS)


@app.route("/questionnaire/<track>")
def questionnaire(track):
    if track not in TRACKS:
        return redirect(url_for("index"))
    session["track"] = track
    session["answers"] = {}
    track_data = TRACKS[track]
    return render_template(
        "questionnaire.html",
        track=track,
        track_data=track_data,
        questions=track_data["questions"],
        total=len(track_data["questions"]),
    )


@app.route("/submit", methods=["POST"])
def submit():
    track = session.get("track")
    if not track:
        return redirect(url_for("index"))

    answers = {}
    track_data = TRACKS[track]
    for q in track_data["questions"]:
        val = request.form.get(q["id"])
        if val:
            answers[q["id"]] = val

    session["answers"] = answers

    # Build skill summary for Watsonx
    skill_summary = []
    for i, q in enumerate(track_data["questions"]):
        ans = answers.get(q["id"], "Not answered")
        skill_summary.append(f"Q: {q['text']}\nA: {ans}")

    session["skill_summary"] = "\n\n".join(skill_summary)
    return redirect(url_for("roadmap"))


@app.route("/roadmap")
def roadmap():
    track = session.get("track")
    skill_summary = session.get("skill_summary")
    if not track or not skill_summary:
        return redirect(url_for("index"))

    track_data = TRACKS[track]
    roadmap_data = generate_roadmap(track_data["label"], skill_summary)
    return render_template(
        "roadmap.html",
        track=track,
        track_data=track_data,
        roadmap=roadmap_data,
    )


@app.route("/api/hint", methods=["POST"])
def hint():
    """Return a short AI hint for a roadmap topic."""
    data = request.get_json()
    topic = data.get("topic", "")
    track = data.get("track", "")
    hint_text = generate_question(track, topic)
    return jsonify({"hint": hint_text})


@app.route("/restart")
def restart():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
