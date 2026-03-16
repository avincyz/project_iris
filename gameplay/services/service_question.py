import random

from ..config.choices import STAGE_TYPE_CHOICES

from ..models import (GameSession,
                      StageRun,
                      QuestionRun,
                      GeneratedQuestion,
                      Playbook)

def generate_questions(session_id, questions_per_stage):
    # get the session based on session_id
    session = GameSession.objects.get(id = session_id)

    incident_type = session.incident_type
    difficulty = session.difficulty

    # TODO: replace below with AI-generated questions/scenarios
    playbook = create_playbook(
        playbook_slug = incident_type,
        difficulty = difficulty
    )

    # create a StageRun for each stage of the scenario listed in STAGE_TYPE_CHOICES
    stage_runs = {}
    for index, stage in enumerate(STAGE_TYPE_CHOICES):
        status = 'active' if index == 0 else 'locked'

        stage_runs[index] = StageRun.objects.create(
            session = session,
            stage_name = stage,
            status = status,
            order_index = index
        )

    for index, stage_run in stage_runs.items():
        stage_name = stage_run.stage_name
        questions = get_stage_questions(playbook, stage_name[1])
        random.shuffle(questions)
        selected_questions = questions[:questions_per_stage]
        snapshot_questions_to_stage(session, stage_run, selected_questions)

def create_playbook(difficulty, playbook_slug, version = 1):
    return Playbook.objects.get(
        slug = playbook_slug,
        difficulty = difficulty,
        version = version,
    )

def get_stage_questions(playbook, stage_name):
    return list(
        GeneratedQuestion.objects.filter(
            playbook = playbook,
            stage_name = stage_name,
            is_active = True
        ).prefetch_related('options')
    )

def snapshot_questions_to_stage(session, stage_run, questions):
    for index, question in enumerate(questions):
        QuestionRun.objects.create(
            session = session,
            stage_name = stage_run.stage_name,
            question_uid = question.question_id,
            question_text = question.prompt,
            options_json = [
                {
                    'id': option.id,
                    'option_uid': option.option_uid,
                    'option_text': option.option_text,
                    'outcome': option.outcome,
                }
                for option in question.options.all()
            ],
            order_index = index,
        )