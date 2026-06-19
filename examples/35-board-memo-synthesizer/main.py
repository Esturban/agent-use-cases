import json

from src.workflow import run

TOPIC = "Proposed acquisition of NovaTech Inc. by MegaCorp Ltd."

REPORTS = [
    (
        "Goldman Sachs Equity Research — NovaTech is a high-growth SaaS platform with 45% YoY ARR growth "
        "and a $2.4B TAM. The acquisition multiple of 8x revenue is fair given the growth trajectory. "
        "Strong recurring revenue base, net revenue retention of 122%, and an expanding partner ecosystem "
        "support a bullish long-term thesis. Management team is experienced and has executed two prior integrations."
    ),
    (
        "Morgan Stanley M&A Advisory — The integration risk is substantial. NovaTech operates on a distinct "
        "technology stack that will require 18-24 months to migrate. Customer concentration risk is high: "
        "top 3 customers represent 38% of ARR. Churn could accelerate post-announcement as competitors "
        "move aggressively. The deal price implies 35x forward EBITDA, leaving minimal margin of safety."
    ),
    (
        "Deloitte Risk Advisory — Regulatory approval timeline is 9-12 months with non-trivial antitrust "
        "risk given MegaCorp's 28% market share. Key-person risk is critical: CEO and CTO are not bound "
        "beyond 12-month retention periods. Data sovereignty issues in the EU product line require "
        "structural remedies. Cyber security posture of NovaTech requires significant uplift before integration."
    ),
]


def main() -> None:
    print(f"Topic: {TOPIC}\n")
    memo = run(TOPIC, REPORTS)

    print(f"RECOMMENDED POSITION: {memo.recommended_position.upper()}")
    print(f"Verdict: {memo.one_sentence_verdict}\n")
    print("--- Executive Summary ---")
    print(memo.executive_summary)
    print()

    for opinion in [memo.bull_case, memo.bear_case, memo.risk_case]:
        print(f"--- {opinion.lens.upper()} CASE (confidence: {opinion.confidence}) ---")
        for point in opinion.key_points:
            print(f"  * {point}")
        print(f"  {opinion.conclusion}")
        print()

    print("Full memo:")
    print(json.dumps(memo.model_dump(), indent=2))


if __name__ == "__main__":
    main()
