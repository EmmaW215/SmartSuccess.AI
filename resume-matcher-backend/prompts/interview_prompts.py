# prompts/interview_prompts.py
"""Prompt templates for interview question generation and feedback"""

SELF_INTRO_QUESTIONS = [
    "Please introduce yourself and give me a brief overview of your professional background.",
    "What interests you about this particular role and our company?",
    "Why are you looking to make a change from your current position?",
    "What makes you the ideal candidate for this position?",
    "What are your greatest professional strengths, and what areas are you working to improve?"
]

TECHNICAL_QUESTION_PROMPT = """Based on this candidate's background and job requirements:

{context}

Generate ONE specific technical interview question that:
1. References a specific skill from their background
2. Relates to the job requirements
3. Asks about challenges or practical application

Question #{question_number} of 5.
Return ONLY the question, no preamble."""

SOFT_SKILL_QUESTION_PROMPT = """Based on this job context:

{context}

Generate ONE behavioral STAR question about: teamwork, communication, or problem-solving.

Question #{question_number} of 5.
Start with "Tell me about a time when..." or "Describe a situation where..."
Return ONLY the question."""

STAR_ANALYSIS_PROMPT = """Analyze this interview response using STAR method.

QUESTION: {question}
RESPONSE: {response}

Rate 1-5 for: activeListening, situation, task, action, result
Identify 2 strengths and 2 growth areas.

Return valid JSON only."""

