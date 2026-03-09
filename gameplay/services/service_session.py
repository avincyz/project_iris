import random

from ..models import GameSession, StageRun, ScenarioSnapshot, QuestionRun


def create_session(user, incident_type, difficulty):

    STAGES = [
        'prepare',
        'detect',
        'analyse',
        'remediate',
        'post_incident',
    ]

    session = GameSession.objects.create(
        user = user,
        incident_type = incident_type,
        difficulty = difficulty,
        status = 'in progress',
    )

    # TODO: AI Integration
    # placeholder scenario snapshot for now
    ScenarioSnapshot.objects.create(
        session = session,
        seed = random.randint(1, 999999),
        scenario_json = {
            'title': 'Placeholder Scenario',
            'incident_type': incident_type,
            'difficulty': difficulty,
        }
    )

    for index, stage in enumerate(STAGES):
        status = 'active' if index == 0 else 'locked'

        StageRun.objects.create(
            session = session,
            stage_name = stage,
            status = status,
            order_index = index
        )

    return session

def get_session_state(session):
    # get the stage from the specified session
    current_stage = StageRun.objects.filter(
        session = session,
        status = 'active'
    ).first()

    # check if stage exists
    if not current_stage:
        return None

    # get the next unanswered question
    next_question = QuestionRun.objects.filter(
        session = session,
        stage_name = current_stage.stage_name,
        is_answered = False
    ).order_by('order_index').first()

    # check if next unanswered question exists
    if not next_question:
        raise ValueError('No unanswered questions detected')
        return None

    return {
        'stage_name': current_stage.stage_name,
        'question_id': next_question.id,
        'question_text': next_question.question_text,
        'options': next_question.options_json,
        'score': session.score,
        'health': session.health
    }

