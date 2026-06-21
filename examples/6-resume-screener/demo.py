"""Gradio demo — resume screener that scores a candidate against a hardcoded backend engineering job spec."""

import os
import sys

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))
from src.schema import ResumeScore  # noqa: E402

SYSTEM_PROMPT = """You are a senior technical recruiter screening candidates for a backend engineering role.

Job Specification:
Role: Senior Python Backend Engineer
Company: FinTech startup (Series B, 80 employees)
Required skills: Python 5+ years, REST API design (FastAPI or Django REST), PostgreSQL or similar relational database, Cloud deployment (AWS or GCP), Git, CI/CD pipelines
Nice to have: Financial domain experience, Pydantic/data validation, Docker/Kubernetes, Team leadership or mentoring
Red flags: Less than 3 years total experience, No production deployment experience, Only frontend or data science work

For each resume, score 1-10. tier: strong_yes=8-10, yes=6-7, maybe=4-5, no=1-3. Be honest about gaps. Do not inflate scores."""

TIER_PREFIX = {
    "strong_yes": "✅ strong_yes",
    "yes": "🟢 yes",
    "maybe": "🟡 maybe",
    "no": "🔴 no",
}

MODELS = [
    "openai/gpt-5.4-nano",
    "minimax/minimax-m3",
    "openai/gpt-4.1-nano",
    "openai/gpt-4o-mini",
    "anthropic/claude-haiku-4-5",
    "google/gemini-flash-1.5",
    "mistralai/mistral-7b-instruct",
]

SAMPLE_ALEX = """Alex Kim
alex.kim@email.com | github.com/alexkim

EXPERIENCE
Senior Backend Engineer — PayFlow Inc (4 years)
- Built and maintained FastAPI microservices handling $2M/day in transaction volume
- Designed PostgreSQL schemas for financial reporting; tuned queries cutting p99 latency by 40%
- Deployed on AWS (ECS, RDS, Lambda); managed CI/CD via GitHub Actions
- Mentored 3 junior engineers; led weekly architecture reviews

Backend Engineer — FinSecure Ltd (3 years)
- Developed Django REST APIs for fraud detection pipelines
- Integrated Pydantic models for strict data validation across payment flows
- Containerized services with Docker and Kubernetes on GCP

SKILLS
Python, FastAPI, Django REST Framework, PostgreSQL, AWS, GCP, Docker, Kubernetes, Pydantic, Git, CI/CD, Redis

EDUCATION
B.S. Computer Science, UC Berkeley"""

SAMPLE_PRIYA = """Priya Sharma
priya.sharma@email.com | github.com/priyasharma | linkedin.com/in/priyasharma

EXPERIENCE
Backend Engineer — NovaBanking (3 years)
- Designed and shipped RESTful APIs in FastAPI for core banking microservices (10M+ requests/day)
- Owns PostgreSQL schema design and query optimization for transaction ledger (TB-scale data)
- Set up and maintains GCP Cloud Run deployment; writes GitHub Actions pipelines
- Domain: payments, KYC, and fraud detection

Software Engineer — InsureTech Co (2 years)
- Python + Django REST Framework for policy administration APIs
- Built Pydantic-based validation layer for third-party insurer data ingestion
- Collaborated with DevOps on Kubernetes migration from on-prem

SKILLS
Python, FastAPI, Django REST Framework, PostgreSQL, GCP (Cloud Run, BigQuery), Docker, Kubernetes, Pydantic, GitHub Actions, Redis, Kafka

EDUCATION
B.Tech Computer Science, IIT Bombay"""

SAMPLE_JORDAN = """Jordan Lee
jordan.lee@email.com

EXPERIENCE
Data Scientist — RetailCo Analytics (4 years)
- Built ML models for demand forecasting using pandas, scikit-learn, and XGBoost
- Created Jupyter notebooks for executive dashboards
- Wrote Python scripts to clean and transform CSV datasets
- Presented model results to non-technical stakeholders

Data Analyst Intern — MarketTrends Inc (6 months)
- Performed exploratory data analysis on customer clickstream data
- Used SQL for ad-hoc queries against Redshift

SKILLS
Python, pandas, scikit-learn, XGBoost, Jupyter, SQL, Tableau, R

EDUCATION
M.S. Statistics, Stanford University"""

SAMPLE_SAM = """Sam Nguyen
sam.nguyen@email.com | linkedin.com/in/samnguyen

EXPERIENCE
Junior Backend Developer — LocalShop (2 years)
- Built Django views and REST endpoints for an e-commerce platform (5k users)
- Wrote basic PostgreSQL queries; used Django ORM for most data access
- Deployed to a shared Linux server via FTP; recently migrating to AWS EC2
- Currently learning GitHub Actions for CI/CD

SKILLS
Python, Django, PostgreSQL, HTML, CSS, Git, basic AWS EC2

EDUCATION
B.S. Information Technology, San Jose State University (2022)"""


def screen_resume(resume_text: str, model: str):
    if not resume_text.strip():
        return None, "", "", "", "", "", ""

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": resume_text},
        ],
        response_format=ResumeScore,
    )

    result: ResumeScore = completion.choices[0].message.parsed

    return (
        result.overall_score,
        TIER_PREFIX.get(result.tier, result.tier),
        ", ".join(result.skills_matched),
        ", ".join(result.skills_missing),
        result.standout,
        result.concern,
        result.recommended_action,
    )


with gr.Blocks(title="Resume Screener") as demo:
    gr.Markdown(
        "## 👤 Resume Screener\n"
        "Paste a resume → the model scores it against a hardcoded job spec and returns a hire tier, "
        "skills gap analysis, and a recommended action in under 5 seconds.\n\n"
        "**Built for:** hiring managers, technical recruiters, and ops leads drowning in applications "
        "who need a consistent, bias-resistant first pass before human review."
    )

    with gr.Accordion("Job Spec & Scoring Rubric", open=True):
        gr.Markdown(
            "**Role:** Senior Python Backend Engineer · Series B FinTech (80 employees)\n\n"
            "| Requirement | Detail |\n"
            "|-------------|--------|\n"
            "| **Required** | Python 5+ yrs · FastAPI or Django REST · PostgreSQL · AWS or GCP · Git/CI/CD |\n"
            "| **Nice to have** | FinTech domain · Pydantic · Docker/Kubernetes · Team leadership |\n"
            "| **Red flags** | <3 yrs experience · No production deployments · Frontend or data-science only |\n\n"
            "**Score → Tier:**\n"
            "- `8–10` = ✅ strong_yes — schedule interview immediately\n"
            "- `6–7` = 🟢 yes — strong candidate, proceed to technical screen\n"
            "- `4–5` = 🟡 maybe — gaps present, worth a quick call to clarify\n"
            "- `1–3` = 🔴 no — does not meet the bar for this role\n\n"
            "_The model never inflates scores. Every gap in the resume vs. the spec is called out explicitly._"
        )

    with gr.Row():
        with gr.Column():
            resume_input = gr.Textbox(
                label="Resume text",
                placeholder="Paste the candidate's resume here…",
                lines=14,
            )
            model_dropdown = gr.Dropdown(
                choices=MODELS,
                value=MODELS[0],
                label="Model",
            )
            screen_btn = gr.Button("Screen Resume", variant="primary")
            gr.Examples(
                examples=[[SAMPLE_ALEX], [SAMPLE_PRIYA], [SAMPLE_JORDAN], [SAMPLE_SAM]],
                inputs=[resume_input],
                label="Sample resumes — click to load",
            )

        with gr.Column():
            gr.Markdown("#### Screening result")
            score_out = gr.Number(label="Score (1–10)")
            tier_out = gr.Textbox(label="Hire tier", interactive=False)
            matched_out = gr.Textbox(label="Skills matched", interactive=False)
            missing_out = gr.Textbox(label="Skills missing", interactive=False)
            standout_out = gr.Textbox(label="What stands out", lines=2, interactive=False)
            concern_out = gr.Textbox(label="Main concern", lines=2, interactive=False)
            action_out = gr.Textbox(label="Recommended action", interactive=False)

    screen_btn.click(
        fn=screen_resume,
        inputs=[resume_input, model_dropdown],
        outputs=[score_out, tier_out, matched_out, missing_out, standout_out, concern_out, action_out],
    )

if __name__ == "__main__":
    demo.launch()
