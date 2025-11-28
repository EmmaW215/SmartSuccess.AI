# services/interview_service.py
"""
Interview Service for SmartSuccess.AI
State machine for managing mock interview flow
"""

import os
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from groq import AsyncGroq
from .rag_service import RAGService


class InterviewSection(Enum):
    GREETING = "greeting"
    MENU = "menu"
    SELF_INTRO = "self_intro"
    TECHNICAL = "technical"
    SOFT_SKILL = "soft_skill"
    COMPLETE = "complete"


@dataclass
class InterviewSession:
    session_id: str
    user_id: str
    current_section: InterviewSection = InterviewSection.GREETING
    question_index: int = 0
    messages: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    job_title: str = ""
    
    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role, "content": content,
            "timestamp": datetime.now().isoformat()
        })


class InterviewService:
    
    SELF_INTRO_QUESTIONS = [
        "Please introduce yourself and give me a brief overview of your background.",
        "Why are you interested in this particular role?",
        "Why are you looking to leave your current position?",
        "What makes you the best fit for this position?",
        "What are your greatest strengths and areas for improvement?"
    ]
    
    def __init__(self):
        self.rag_service = RAGService()
        groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = AsyncGroq(api_key=groq_key) if groq_key else None
        self.sessions: Dict[str, InterviewSession] = {}
    
    async def create_session(self, session_id: str, user_id: str) -> InterviewSession:
        session = InterviewSession(session_id=session_id, user_id=user_id)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return self.sessions.get(session_id)
    
    async def get_greeting(self) -> str:
        return (
            "Welcome to your Mock Interview!\n\n"
            "I'm your AI interviewer today. I've reviewed your resume and job requirements.\n\n"
            "When you're ready, just say 'I'm ready' or 'Yes'."
        )
    
    async def get_menu(self) -> str:
        return (
            "Please choose an interview section:\n\n"
            "1. Self-Introduction - Tell me about yourself\n"
            "2. Technical Questions - Based on your skills\n"
            "3. Soft-Skill Questions - Behavioral questions\n\n"
            "Say the number or section name. Say 'STOP' to return here."
        )
    
    async def process_message(self, session_id: str, user_message: str) -> Dict:
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        session.add_message("user", user_message)
        
        if "stop" in user_message.lower():
            session.current_section = InterviewSection.MENU
            session.question_index = 0
            response = "Let's take a break.\n\n" + await self.get_menu()
            session.add_message("assistant", response)
            return {"response": response, "section": session.current_section.value}
        
        response = ""
        
        if session.current_section == InterviewSection.GREETING:
            if self._is_ready(user_message):
                session.current_section = InterviewSection.MENU
                response = await self.get_menu()
            else:
                response = "Let me know when you're ready!"
        
        elif session.current_section == InterviewSection.MENU:
            section = self._parse_section_choice(user_message)
            if section:
                session.current_section = section
                session.question_index = 0
                response = await self._get_next_question(session)
            else:
                response = "Please say 1, 2, or 3."
        
        else:
            feedback = await self._generate_feedback(session, user_message)
            session.question_index += 1
            
            if session.question_index >= 5:
                session.current_section = InterviewSection.MENU
                session.question_index = 0
                response = f"{feedback}\n\nSection complete! " + await self.get_menu()
            else:
                next_q = await self._get_next_question(session)
                response = f"{feedback}\n\n---\n\n{next_q}"
        
        session.add_message("assistant", response)
        return {"response": response, "section": session.current_section.value, "question_index": session.question_index}
    
    async def _get_next_question(self, session: InterviewSession) -> str:
        if session.current_section == InterviewSection.SELF_INTRO:
            if session.question_index < len(self.SELF_INTRO_QUESTIONS):
                return self.SELF_INTRO_QUESTIONS[session.question_index]
            return "Tell me about your career goals."
        
        elif session.current_section == InterviewSection.TECHNICAL:
            context = await self.rag_service.get_technical_context(session.user_id)
            prompt = f"Based on: {context}\n\nGenerate ONE technical interview question. Return ONLY the question."
            return await self._call_llm(prompt)
        
        elif session.current_section == InterviewSection.SOFT_SKILL:
            context = await self.rag_service.get_soft_skills_context(session.user_id)
            prompt = f"Based on: {context}\n\nGenerate ONE behavioral STAR question. Return ONLY the question."
            return await self._call_llm(prompt)
        
        return "Tell me more about your experience."
    
    async def _generate_feedback(self, session: InterviewSession, answer: str) -> str:
        prompt = f"Give brief encouraging feedback (2 sentences) on this answer: {answer[:500]}"
        return await self._call_llm(prompt)
    
    async def _call_llm(self, prompt: str) -> str:
        if not self.groq_client:
            return "That's a great point. Can you elaborate?"
        try:
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a professional interview coach."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300, temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM error: {e}")
            return "That's interesting. Tell me more."
    
    def _is_ready(self, message: str) -> bool:
        ready = ["ready", "yes", "start", "begin", "ok", "okay", "sure"]
        return any(r in message.lower() for r in ready)
    
    def _parse_section_choice(self, message: str) -> Optional[InterviewSection]:
        msg = message.lower()
        if "1" in msg or "self" in msg or "intro" in msg:
            return InterviewSection.SELF_INTRO
        elif "2" in msg or "tech" in msg:
            return InterviewSection.TECHNICAL
        elif "3" in msg or "soft" in msg or "behavior" in msg:
            return InterviewSection.SOFT_SKILL
        return None

