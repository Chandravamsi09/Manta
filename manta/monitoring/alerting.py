from __future__ import annotations
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from manta.monitoring.statistical import DriftReport
from manta.core.logging import get_logger

logger = get_logger("monitoring_alerting")

class AlertChannel(ABC):
    @abstractmethod
    def send_alert(self, title: str, report: DriftReport) -> None:
        pass


class WebhookAlertChannel(AlertChannel):
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url

    def send_alert(self, title: str, report: DriftReport) -> None:
        logger.warning(f"[WEBHOOK ALERT -> {self.endpoint_url}] {title} | Feature: {report.feature_name} | Drift: {report.metric_value}")


class RetrainingTrigger:
    """Dispatches automated retraining pipeline events upon drift confirmation."""
    def __init__(self, pipeline_runner: Optional[Any] = None):
        self.pipeline_runner = pipeline_runner

    def trigger_retraining(self, model_name: str, reason: str) -> str:
        job_id = f"retrain_{model_name}_{int(__import__('time').time())}"
        logger.info(f"Triggered Automated Retraining Job '{job_id}' for model '{model_name}'. Reason: {reason}")
        return job_id


class AlertManager:
    """Dispatches alerts to configured channels."""
    def __init__(self):
        self._channels: List[AlertChannel] = []

    def add_channel(self, channel: AlertChannel) -> None:
        self._channels.append(channel)

    def dispatch(self, report: DriftReport) -> None:
        if report.drift_detected:
            for ch in self._channels:
                ch.send_alert(f"Model Drift Detected in feature '{report.feature_name}'", report)
