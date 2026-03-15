import random
from typing import Dict, List, Optional

from gameplay.models import Playbook, GeneratedQuestion

PHASES_IN_ORDER = ["Prepare", "Detect", "Analyse", "Remediation", "Post-Incident"]


def pick_playbook(*, difficulty: str, playbook_slug: str, version: int = 1) -> Playbook:
    return Playbook.objects.get(slug=playbook_slug, difficulty=difficulty, version=version)


def build_stage_question_pack(
    *,
    playbook: Playbook,
    questions_per_stage: int = 2,
    seed: Optional[int] = None,
) -> Dict[str, List[GeneratedQuestion]]:
    rng = random.Random(seed)
    pack: Dict[str, List[GeneratedQuestion]] = {}

    for phase in PHASES_IN_ORDER:
        qs = list(
            GeneratedQuestion.objects.filter(
                playbook=playbook,
                phase=phase,
                is_active=True,
            ).prefetch_related("options")
        )

        rng.shuffle(qs)

        if len(qs) < questions_per_stage:
            raise ValueError(
                f"Not enough questions for phase '{phase}'. "
                f"Need {questions_per_stage}, found {len(qs)}."
            )

        pack[phase] = qs[:questions_per_stage]

    return pack


def serialize_question(q: GeneratedQuestion) -> dict:
    return {
        "external_id": q.external_id,
        "phase": q.phase,
        "prompt": q.prompt,
        "options": [
            {"label": o.label, "text": o.text, "outcome": o.outcome}
            for o in q.options.all()
        ],
    }


def serialize_stage_pack(stage_pack: Dict[str, List[GeneratedQuestion]]) -> dict:
    return {phase: [serialize_question(q) for q in qs] for phase, qs in stage_pack.items()}