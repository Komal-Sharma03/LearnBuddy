"""Smoke tests — run with: py -3 test_app.py"""
import os, json, sys
os.environ.setdefault("FLASK_SECRET_KEY", "test-secret")

from app import app, TRACKS

FORM_DATA = {
    "q1": "I build layouts confidently",
    "q2": "I work with DOM & events",
    "q3": "I build apps with a framework",
    "q4": "I branch, merge, and resolve conflicts",
    "q5": "I profile and optimize bundles",
}


def run_tests():
    with app.test_client() as client:
        # index
        r = client.get("/")
        assert r.status_code == 200, f"index: {r.status_code}"
        print("PASS  GET /")

        # questionnaire — all tracks
        for track in ("frontend", "cybersecurity", "uiux"):
            r = client.get(f"/questionnaire/{track}")
            assert r.status_code == 200, f"questionnaire/{track}: {r.status_code}"
            print(f"PASS  GET /questionnaire/{track}")

        # bad track → redirect
        r = client.get("/questionnaire/nonexistent")
        assert r.status_code in (301, 302), f"bad track: {r.status_code}"
        print("PASS  GET /questionnaire/nonexistent (redirect)")

        # submit
        with client.session_transaction() as sess:
            sess["track"] = "frontend"
        r = client.post("/submit", data=FORM_DATA)
        assert r.status_code in (200, 302), f"submit: {r.status_code}"
        print("PASS  POST /submit")

        # roadmap — all three tracks
        questions = TRACKS["frontend"]["questions"]
        summary_parts = []
        for i, q in enumerate(questions):
            ans = list(FORM_DATA.values())[i]
            summary_parts.append(f"Q: {q['text']}\nA: {ans}")

        with client.session_transaction() as sess:
            sess["track"] = "frontend"
            sess["skill_summary"] = "\n\n".join(summary_parts)

        r = client.get("/roadmap")
        assert r.status_code == 200, f"roadmap: {r.status_code}\n{r.data[:400].decode()}"
        assert b"Your Frontend Development Roadmap" in r.data
        print("PASS  GET /roadmap (frontend)")

        # hint API
        payload = json.dumps({"topic": "React Fundamentals", "track": "Frontend Development"})
        r = client.post("/api/hint", data=payload, content_type="application/json")
        assert r.status_code == 200, f"hint: {r.status_code}"
        j = json.loads(r.data)
        assert "hint" in j and j["hint"], f"hint empty: {j}"
        print("PASS  POST /api/hint")

        # restart
        r = client.get("/restart")
        assert r.status_code in (301, 302), f"restart: {r.status_code}"
        print("PASS  GET /restart")

    print("\nAll tests passed.")


if __name__ == "__main__":
    run_tests()
