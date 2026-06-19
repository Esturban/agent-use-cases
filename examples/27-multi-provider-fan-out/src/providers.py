from openai import OpenAI

from .prompts import OPINION_SYSTEM, SYNTHESIS_SYSTEM
from .schema import ModelConsensus, StrategicOpinion

MODELS = [
    "openai/gpt-4o-mini",
    "mistralai/mistral-7b-instruct",
    "meta-llama/llama-3.1-8b-instruct",
]

SYNTHESIS_MODEL = "openai/gpt-4o-mini"


def query_model(client: OpenAI, model: str, topic: str) -> StrategicOpinion:
    """Query a single model for a strategic opinion on the given topic."""
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": OPINION_SYSTEM},
            {"role": "user", "content": f"Topic: {topic}"},
        ],
        response_format=StrategicOpinion,
    )
    opinion: StrategicOpinion = completion.choices[0].message.parsed
    opinion.model = model
    return opinion


def synthesise(client: OpenAI, topic: str, opinions: list[StrategicOpinion]) -> ModelConsensus:
    """Synthesise multiple opinions into a single consensus view."""
    opinions_text = "\n\n".join(
        f"Model: {o.model}\n"
        f"Recommendation: {o.recommendation}\n"
        f"Risks: {', '.join(o.key_risks)}\n"
        f"Opportunities: {', '.join(o.key_opportunities)}\n"
        f"Confidence: {o.confidence}"
        for o in opinions
    )
    completion = client.beta.chat.completions.parse(
        model=SYNTHESIS_MODEL,
        messages=[
            {"role": "system", "content": SYNTHESIS_SYSTEM},
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nOpinions:\n{opinions_text}",
            },
        ],
        response_format=ModelConsensus,
    )
    consensus: ModelConsensus = completion.choices[0].message.parsed
    consensus.topic = topic
    consensus.opinions = opinions
    return consensus
