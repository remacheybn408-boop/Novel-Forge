"""
Base agent class for multi-agent review system.
Placeholder only — not enabled in v0.5.0.
"""

class BaseAgent:
    """Minimal base agent interface for future multi-agent systems."""
    
    def __init__(self, name: str, config: dict = None):
        self.name = name
        self.config = config or {}
        self.enabled = False  # Always disabled by default
    
    def review(self, content: str, context: dict = None) -> dict:
        """Review content and return findings."""
        return {"status": "DISABLED", "reason": "Multi-agent not enabled in v0.5.0"}
