"""
Application-level detection service.

Thin wrapper around DetectionEngine. Exists so the API layer has a
stable service interface even if the engine is swapped later.
"""

from __future__ import annotations

from app.attacks.contracts import DetectionOutcome, VerificationContext
from app.detection.engine import DetectionEngine


class DetectionService:
    """
    Application-level detection service.
    Combines deterministic verification checks and 
    returns a structured DetectionOutcome.
    """

    def __init__(self, engine: DetectionEngine | None = None) -> None:
        self._engine = engine or DetectionEngine()

    def detect(self, context: VerificationContext) -> DetectionOutcome:
        return self._engine.verify(context)