# flexiai/core/__init__.py
from flexiai.core.flexiai_client import FlexiAI
from flexiai.core.flexi_managers.multi_agent_system import MultiAgentSystemManager

__all__ = [
    'FlexiAI',
    'MultiAgentSystemManager',
]
