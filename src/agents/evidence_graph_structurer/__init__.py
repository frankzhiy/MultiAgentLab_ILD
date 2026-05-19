"""Public package for the Evidence Graph Structurer agent.

Only the public agent class is exported. Internal pipeline classes, module
classes, and schemas live under their respective subpackages.
"""

from .agent import EvidenceGraphStructurerAgent

__all__ = ["EvidenceGraphStructurerAgent"]
