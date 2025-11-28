# services/feedback_service.py
"""
STAR Method Feedback Service for SmartSuccess.AI
"""

import os
import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter
from groq import AsyncGroq
import openai


@dataclass
class STARScore:
    situation: int = 0
    task: int = 0
    action: int = 0
    result: int = 0
    
    @property
    def average(self) -> float:
        scores = [self.situation, self.task, self.action, self.result]
        return sum(scores) / len(scores) if any(scores) else 0
    
    def to_dict(self) -> Dict:
        return {
            "situation": self.situation, "task": self.task,
            "action": self.action, "result": self.result,
            "average": round(self.average, 1)
        }


@dataclass
class DeliveryMetrics:
    filler_words: int = 0
    word_count: int = 0
    speaking_time_seconds: float = 0
    pacing: str = "good"
    
    def to_dict(self) -> Dict:
        return {
            "fillerWords": self.filler_words, "wordCount": self.word_count,
            "speakingTime": round(self.speaking_time_seconds, 1), "pacing": self.pacing
        }


@dataclass
class QuestionFeedback:
    question: str
    response: str
    timestamp: str
    active_listening_score: int = 0
    active_listening_insight: str = ""
    star_score: STARScore = field(default_factory=STARScore)
    star_insights: Dict[str, str] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    growth_areas: List[str] = field(default_factory=list)
    delivery: DeliveryMetrics = field(default_factory=DeliveryMetrics)
    
    def to_dict(self) -> Dict:
        return {
            "question": self.question, "response": self.response,
            "timestamp": self.timestamp,
            "activeListening": {"score": self.active_listening_score, "insight": self.active_listening_insight},
            "starScore": self.star_score.to_dict(),
            "starInsights": self.star_insights,
            "strengths": self.strengths, "growthAreas": self.growth_areas,
            "delivery": self.delivery.to_dict()
        }


@dataclass
class SessionFeedback:
    session_id: str
    user_id: str
    job_title: str = ""
    overall_score: float = 0.0
    questions_feedback: List[QuestionFeedback] = field(default_factory=list)
    aggregated_strengths: List[str] = field(default_factory=list)
    aggregated_growth_areas: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def calculate_overall_score(self) -> float:
        if not self.questions_feedback:
            return 0.0
        total = sum((qf.active_listening_score * 0.2) + (qf.star_score.average * 0.8) 
                    for qf in self.questions_feedback)
        avg = total / len(self.questions_feedback)
        self.overall_score = round((avg / 5) * 100, 1)
        return self.overall_score
    
    def to_dict(self) -> Dict:
        return {
            "sessionId": self.session_id, "userId": self.user_id,
            "jobTitle": self.job_title, "overallScore": self.overall_score,
            "questionsFeedback": [qf.to_dict() for qf in self.questions_feedback],
            "aggregatedStrengths": self.aggregated_strengths,
            "aggregatedGrowthAreas": self.aggregated_growth_areas,
            "createdAt": self.created_at
        }


class FeedbackService:
    FILLER_WORDS = ["um", "uh", "like", "you know", "basically", "actually", "literally", "honestly"]
    
    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = AsyncGroq(api_key=groq_key) if groq_key else None
        openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = openai.AsyncOpenAI(api_key=openai_key) if openai_key else None
        self.session_feedback: Dict[str, SessionFeedback] = {}
    
    async def analyze_response(
        self, session_id: str, user_id: str, question: str,
        response: str, job_context: Optional[str] = None
    ) -> QuestionFeedback:
        feedback = QuestionFeedback(
            question=question, response=response,
            timestamp=datetime.now().isoformat()
        )
        feedback.delivery = self._analyze_delivery(response)
        ai_feedback = await self._get_ai_feedback(question, response, job_context)
        
        feedback.active_listening_score = ai_feedback.get("activeListening", {}).get("score", 3)
        feedback.active_listening_insight = ai_feedback.get("activeListening", {}).get("insight", "")
        feedback.star_score = STARScore(
            situation=ai_feedback.get("situation", {}).get("score", 3),
            task=ai_feedback.get("task", {}).get("score", 3),
            action=ai_feedback.get("action", {}).get("score", 3),
            result=ai_feedback.get("result", {}).get("score", 3)
        )
        feedback.star_insights = {k: ai_feedback.get(k, {}).get("insight", "") 
                                   for k in ["situation", "task", "action", "result"]}
        feedback.strengths = ai_feedback.get("strengths", [])
        feedback.growth_areas = ai_feedback.get("growthAreas", [])
        
        if session_id not in self.session_feedback:
            self.session_feedback[session_id] = SessionFeedback(session_id=session_id, user_id=user_id)
        self.session_feedback[session_id].questions_feedback.append(feedback)
        return feedback
    
    def _analyze_delivery(self, text: str) -> DeliveryMetrics:
        metrics = DeliveryMetrics()
        words = text.split()
        metrics.word_count = len(words)
        text_lower = text.lower()
        for filler in self.FILLER_WORDS:
            metrics.filler_words += text_lower.count(filler)
        metrics.speaking_time_seconds = (metrics.word_count / 150) * 60
        metrics.pacing = "too_brief" if metrics.word_count < 50 else "too_long" if metrics.word_count > 350 else "good"
        return metrics
    
    async def _get_ai_feedback(self, question: str, response: str, job_context: Optional[str] = None) -> Dict:
        ctx = f"JOB CONTEXT: {job_context}" if job_context else ""
        prompt = f'''Analyze this interview response. Rate 1-5 for each STAR category.
QUESTION: {question}
RESPONSE: {response}
{ctx}

Return JSON only:
{{"activeListening": {{"score": 3, "insight": "..."}}, "situation": {{"score": 3, "insight": "..."}}, "task": {{"score": 3, "insight": "..."}}, "action": {{"score": 3, "insight": "..."}}, "result": {{"score": 3, "insight": "..."}}, "strengths": ["...", "..."], "growthAreas": ["...", "..."]}}'''

        if self.groq_client:
            try:
                resp = await self.groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[{"role": "system", "content": "Return only valid JSON."},
                              {"role": "user", "content": prompt}],
                    max_tokens=500, temperature=0.3
                )
                return self._parse_json(resp.choices[0].message.content.strip())
            except Exception as e:
                print(f"Groq error: {e}")
        
        if self.openai_client:
            try:
                resp = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Return only valid JSON."},
                              {"role": "user", "content": prompt}],
                    max_tokens=500, temperature=0.3
                )
                return self._parse_json(resp.choices[0].message.content.strip())
            except Exception as e:
                print(f"OpenAI error: {e}")
        
        return self._default_feedback()
    
    def _parse_json(self, text: str) -> Dict:
        try:
            text = re.sub(r'^[\s\S]*?\{', '{', text, count=1)
            text = re.sub(r'\}[\s\S]*$', '}', text, count=1)
            return json.loads(text)
        except:
            return self._default_feedback()
    
    def _default_feedback(self) -> Dict:
        return {
            "activeListening": {"score": 3, "insight": "Response noted."},
            "situation": {"score": 3, "insight": "Context provided."},
            "task": {"score": 3, "insight": "Role explained."},
            "action": {"score": 3, "insight": "Actions described."},
            "result": {"score": 3, "insight": "Outcomes mentioned."},
            "strengths": ["Clear communication", "Relevant example"],
            "growthAreas": ["Add specifics", "Quantify results"]
        }
    
    def get_session_summary(self, session_id: str) -> Optional[SessionFeedback]:
        if session_id not in self.session_feedback:
            return None
        session = self.session_feedback[session_id]
        session.calculate_overall_score()
        all_strengths = [s for qf in session.questions_feedback for s in qf.strengths]
        all_growth = [g for qf in session.questions_feedback for g in qf.growth_areas]
        session.aggregated_strengths = [i for i, _ in Counter(all_strengths).most_common(3)]
        session.aggregated_growth_areas = [i for i, _ in Counter(all_growth).most_common(3)]
        return session

