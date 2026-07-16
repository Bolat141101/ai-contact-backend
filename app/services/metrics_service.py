from app.repositories.metrics_repository import MetricsRepository


class MetricsService:
    def __init__(self, repository: MetricsRepository | None = None):
        self.repository = repository or MetricsRepository()

    def get_summary(self) -> dict:
        return self.repository.get_summary()
