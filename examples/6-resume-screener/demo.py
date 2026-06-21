"""Gradio demo — resume screener that scores a candidate against a hardcoded backend engineering job spec."""

import os

import gradio as gr
from openai import OpenAI

from src.schema import ResumeScore

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
        api_key=os.environ["OPENROUTER_API_KEY"],
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
    gr.Markdown("## Resume Screener — Senior Python Backend Engineer")

    with gr.Row():
        with gr.Column():
            resume_input = gr.Textbox(
                label="Resume Text",
                placeholder="Paste the candidate's resume here…",
                lines=12,
            )
            model_dropdown = gr.Dropdown(
                choices=MODELS,
                value=MODELS[0],
                label="Model",
            )
            screen_btn = gr.Button("Screen Resume", variant="primary")
            gr.Examples(
                examples=[
                    [SAMPLE_ALEX, MODELS[0]],
                    [SAMPLE_JORDAN, MODELS[0]],
                    [SAMPLE_SAM, MODELS[0]],
                ],
                inputs=[resume_input, model_dropdown],
                label="Sample Resumes",
            )

        with gr.Column():
            score_out = gr.Number(label="Overall Score (1–10)")
            tier_out = gr.Textbox(label="Tier")
            matched_out = gr.Textbox(label="Skills Matched")
            missing_out = gr.Textbox(label="Skills Missing")
            standout_out = gr.Textbox(label="Standout")
            concern_out = gr.Textbox(label="Concern")
            action_out = gr.Textbox(label="Recommended Action")

    screen_btn.click(
        fn=screen_resume,
        inputs=[resume_input, model_dropdown],
        outputs=[score_out, tier_out, matched_out, missing_out, standout_out, concern_out, action_out],
    )

if __name__ == "__main__":
    demo.launch()
