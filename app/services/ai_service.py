from dataclasses import dataclass
from typing import Literal

from flask import current_app
from openai import OpenAI
from pydantic import BaseModel, Field

from app.prompts.contact_analysis import CONTACT_ANALYSIS_PROMPT

DEFAULT_REPLY = "Спасибо за обращение. Я получил ваше сообщение и свяжусь с вами в ближайшее время."


class AIAnalysisPayload(BaseModel):
    category: Literal["project_request", "job_offer", "consultation", "support", "spam", "other"]
    sentiment: Literal["positive", "neutral", "negative"]
    priority: Literal["low", "normal", "high"]
    reply_draft: str = Field(min_length=1, max_length=600)


@dataclass(frozen=True)
class AIAnalysis:
    category: str
    sentiment: str
    priority: str
    reply_draft: str
    processed: bool
    status: str


class AIService:
    def analyze(self, comment: str) -> AIAnalysis:
        api_key = current_app.config["OPENAI_API_KEY"]
        if not api_key:
            return self._fallback("disabled")

        try:
            client = OpenAI(
                api_key=api_key,
                timeout=current_app.config["AI_TIMEOUT_SECONDS"],
            )
            response = client.responses.parse(
                model=current_app.config["OPENAI_MODEL"],
                input=[
                    {"role": "system", "content": CONTACT_ANALYSIS_PROMPT},
                    {"role": "user", "content": comment},
                ],
                text_format=AIAnalysisPayload,
            )
            result = response.output_parsed
            if result is None:
                raise ValueError("AI response did not contain parsed output")
            return AIAnalysis(
                category=result.category,
                sentiment=result.sentiment,
                priority=result.priority,
                reply_draft=result.reply_draft,
                processed=True,
                status="success",
            )
        except Exception:
            current_app.logger.exception("ai_analysis_failed")
            return self._fallback("fallback")

    @staticmethod
    def _fallback(status: str) -> AIAnalysis:
        return AIAnalysis(
            category="other",
            sentiment="neutral",
            priority="normal",
            reply_draft=DEFAULT_REPLY,
            processed=False,
            status=status,
        )
