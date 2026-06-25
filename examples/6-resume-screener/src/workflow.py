from langchain_openai import ChatOpenAI

from .prompts import SYSTEM_PROMPT
from .schema import ResumeScore


def create_screener():
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
    return SYSTEM_PROMPT | llm.with_structured_output(ResumeScore)


def screen(resume_text: str) -> ResumeScore:
    screener = create_screener()
    return screener.invoke(resume_text)
