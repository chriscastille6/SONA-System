"""
AI Agents for IRB Review

Each agent specializes in a specific aspect of ethical review.
"""

from .base import BaseAgent
from .ethics import EthicsAgent
from .privacy import PrivacyAgent
from .vulnerability import VulnerabilityAgent
from .data_security import DataSecurityAgent
from .consent import ConsentAgent

__all__ = [
    'BaseAgent',
    'EthicsAgent',
    'PrivacyAgent',
    'VulnerabilityAgent',
    'DataSecurityAgent',
    'ConsentAgent',
]








