"""
Multi-provider fan-out -- same prompt, multiple models, one consensus.

Step 1: Send the strategic brief to N models in parallel via OpenRouter.
Step 2: Collect typed StrategicOpinion from each model.
Step 3: A synthesis model produces a ModelConsensus from all opinions.

All models accessed through OpenRouter -- swap model strings freely.
"""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

from .schema import ModelConsensus, StrategicOpinion

MODELS = [
    "openai/gpt-4o-mini",
    "mistralai/mistral-7b-instruct",
    "meta-llama/llama-3.1-8b-instruct",
]

SYNTHESIS_MODEL = "openai/gpt-4o-mini"

_OPINION_SYSTEM = (
    "You are a strategic advisor. Given a business topic, provide:\n"
    "- A concise recommendation (1-2 sentences)\n"
    "- Up to 3 key risks\n"
    "- Up to 3 key opportunities\n"
    "- Your confidence level: high, medium, or low\n"
    "Be specific and direct. No hedging."
)

_SYNTHESIS_SYSTEM = (
    "You are a senior analyst synthesising multiple strategic opinions into one consensus view. "
    "Identify where the models agree, where they diverge, and produce a single consolidated "
    "recommendation that reflects the majority position. Be specific."
)


def _query_model(client: OpenAI, model: str, topic: str) -> StrategicOpinion:
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": _OPINION_SYSTEM},
            {"role": "user", "content": f"Topic: {topic}"},
        ],
        response_format=StrategicOpinion,
    )
    opinion: StrategicOpinion = completion.choices[0].message.parsed
    opinion.model = model
    return opinion


def _synthesise(client: OpenAI, topic: str, opinions: list[StrategicOpinion]) -> ModelConsensus:
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
            {"role": "system", "content": _SYNTHESIS_SYSTEM},
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


def run(topic: str, models: list[str] | None = None) -> ModelConsensus:
    """Query multiple models in parallel and synthesise a consensus."""
    selected_models = models or MODELS
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )

    opinions: list[StrategicOpinion] = []
    with ThreadPoolExecutor(max_workers=len(selected_models)) as executor:
        futures = {
            executor.submit(_query_model, client, model, topic): model
            for model in selected_models
        }
        for future in as_completed(futures):
            opinions.append(future.result())

    opinions.sort(key=lambda o: selected_models.index(o.model))
    return _synthesise(client, topic, opinions)
