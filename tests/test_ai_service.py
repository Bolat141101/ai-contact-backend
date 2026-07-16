from types import SimpleNamespace

from app.services.ai_service import AIAnalysisPayload, AIService


class FakeResponses:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def parse(self, **kwargs):
        if self.error:
            raise self.error
        return SimpleNamespace(output_parsed=self.result)


class FakeOpenAI:
    responses = FakeResponses(
        result=AIAnalysisPayload(
            category="project_request",
            sentiment="positive",
            priority="high",
            reply_draft="Спасибо! Я изучу детали вашего проекта.",
        )
    )

    def __init__(self, **kwargs):
        pass


def test_ai_service_returns_structured_result(app, monkeypatch):
    monkeypatch.setattr("app.services.ai_service.OpenAI", FakeOpenAI)

    with app.app_context():
        app.config["OPENAI_API_KEY"] = "test-key"
        result = AIService().analyze("Хочу заказать разработку сайта")

    assert result.processed is True
    assert result.status == "success"
    assert result.category == "project_request"
    assert result.priority == "high"


def test_ai_service_falls_back_on_provider_error(app, monkeypatch):
    class FailingOpenAI(FakeOpenAI):
        responses = FakeResponses(error=TimeoutError("provider timed out"))

    monkeypatch.setattr("app.services.ai_service.OpenAI", FailingOpenAI)

    with app.app_context():
        app.config["OPENAI_API_KEY"] = "test-key"
        result = AIService().analyze("Any message")

    assert result.processed is False
    assert result.status == "fallback"
    assert result.category == "other"
    assert result.reply_draft
