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

from .providers import MODELS, query_model, synthesise
from .schema import ModelConsensus


def run(topic: str, models: list[str] | None = None) -> ModelConsensus:
    """Query multiple models in parallel and synthesise a consensus."""
    selected_models = models or MODELS
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )

    opinions = []
    with ThreadPoolExecutor(max_workers=len(selected_models)) as executor:
        futures = {
            executor.submit(query_model, client, model, topic): model
            for model in selected_models
        }
        for future in as_completed(futures):
            opinions.append(future.result())

    opinions.sort(key=lambda o: selected_models.index(o.model))
    return synthesise(client, topic, opinions)
