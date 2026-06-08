PREDICTION_EXPLANATION_PROMPT = """
Explain the predictive maintenance result in simple maintenance language.
Use only the provided context. Do not invent SAP orders, dates, people, or root
causes. Do not decide risk; explain the backend decision from ML, rules,
maintenance planning, and retrieved history. Keep the explanation short,
practical, and clear about what technicians should check next. If confidence is
low, say so.
"""

MAINTENANCE_RECOMMENDATION_PROMPT = """
Summarize practical maintenance actions for technicians using only known failure
causes, previous work orders, checklists, and expert notes provided in context.
Do not exaggerate. Focus on what to check and what to do next.
"""

SIMILAR_FAILURE_SUMMARY_PROMPT = """
Summarize similar historical failures with symptom, likely cause, action taken,
and lesson learned for the selected industrial asset.
"""

FAILURE_EXPLANATION_PROMPT = PREDICTION_EXPLANATION_PROMPT
SIMILAR_CASE_SUMMARY_PROMPT = SIMILAR_FAILURE_SUMMARY_PROMPT

FALLBACK_EXPLANATION_PROMPT = (
    "Explain predictive maintenance results in plain language for maintenance technicians. "
    "The LLM explains; it does not decide risk."
)
