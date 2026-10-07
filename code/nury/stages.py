"""Compatibility shim. Stages now live in code/playbooks/<id>/stages.json.

STAGES and REGISTRY give the default (detention) playbook's stages.
Use nury.engine.get_playbook(id) for any other playbook.
"""

from .engine import DEFAULT_PLAYBOOK, get_playbook

_PB = get_playbook(DEFAULT_PLAYBOOK)
STAGES = _PB.stages
REGISTRY = _PB.registry
