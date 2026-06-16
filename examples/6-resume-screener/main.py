from dotenv import load_dotenv

from src.workflow import screen

load_dotenv()

RESUMES = [
    {
        "name": "Alex Kim",
        "text": """Alex Kim — Senior Software Engineer
7 years Python. Built REST APIs with FastAPI at two fintech startups.
Led a team of 3 engineers. PostgreSQL, Redis, AWS (ECS, RDS).
Deployed to production weekly using GitHub Actions + Docker.
Currently at PayScale Inc, handling $2M/day transaction volume.
Skills: Python, FastAPI, PostgreSQL, AWS, Docker, Pydantic, Git.""",
    },
    {
        "name": "Jordan Lee",
        "text": """Jordan Lee — Data Scientist
4 years total experience. Python, pandas, scikit-learn, Jupyter.
Built ML pipelines for e-commerce recommendation system.
Some Flask API work (internal tools only, never production).
No cloud deployment. Mostly data science and analytics.
Skills: Python, pandas, scikit-learn, SQL (basic), Flask.""",
    },
    {
        "name": "Sam Nguyen",
        "text": """Sam Nguyen — Backend Developer
2 years experience. Django REST Framework, PostgreSQL.
Junior role at a startup. Worked on user auth and CRUD endpoints.
Some GCP experience (App Engine). No team leadership.
Still learning Docker and CI/CD.
Skills: Python, Django, PostgreSQL, GCP (basic), Git.""",
    },
]


def main():
    print("RESUME SCREENING RESULTS")
    print("=" * 60)

    results = []
    for r in RESUMES:
        result = screen(r["text"])
        results.append(result)
        print(f"\n{result.candidate_name}")
        print(f"  Score:    {result.overall_score}/10  |  Tier: {result.tier}")
        print(f"  Action:   {result.recommended_action}")
        print(f"  Matched:  {', '.join(result.skills_matched)}")
        print(f"  Missing:  {', '.join(result.skills_missing)}")
        print(f"  Standout: {result.standout}")
        print(f"  Concern:  {result.concern}")

    print("\n" + "=" * 60)
    print("RANKING")
    ranked = sorted(results, key=lambda x: x.overall_score, reverse=True)
    for i, r in enumerate(ranked, 1):
        print(f"  {i}. {r.candidate_name:15} {r.overall_score}/10  {r.tier}")


if __name__ == "__main__":
    main()
