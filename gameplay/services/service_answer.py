from django.db import transaction
from django.utils import timezone

from ..config.score_sheet import OUTCOME_SCORES, OUTCOME_HEALTH_CHANGES, DIFFICULTY_MODIFIER
from ..models import GameSession, QuestionRun, StageRun

def process_answer(session_id, question_uid, selected_option_id):
    session = GameSession.objects.get(
        id = session_id,
    )
    if not session:
        raise ValueError('Specified session not found')
    if session.status != 'in progress':
        raise ValueError('Session is not in progress')

    question = QuestionRun.objects.get(
        session=session,
        question_uid=question_uid
    )
    if not question:
        raise ValueError('Specified question not found')
    if question.is_answered:
        raise ValueError('Question has already been answered')

    stage = StageRun.objects.get(
        session = session,
        stage_name = question.stage_name,
    )
    if not stage:
        raise ValueError('Specified stage not found')
    if stage.status != 'active':
        raise ValueError('Stage is not active')

    with transaction.atomic():
        difficulty = session.difficulty
        diff_modifier = DIFFICULTY_MODIFIER.get(difficulty, 1.0)

        options = question.options_json
        selected_option = None

        for option in options:
            if selected_option_id == option['option_uid']:
                selected_option = option
                break

        if not selected_option:
            raise ValueError('Specified option not found')

        outcome = selected_option['outcome']

        # check how much health will change based on answer
        health_change = OUTCOME_HEALTH_CHANGES.get(outcome, 0)
        # if penalty (negative change), apply difficulty modifier
        if health_change < 0:
            health_change *= diff_modifier
            health_change = round(health_change, 2)

        # check how much score will change based on answer
        score_change = OUTCOME_SCORES.get(outcome, 0)
        # if penalty (negative change), apply difficulty modifier
        if score_change < 0:
            score_change *= diff_modifier
            score_change = round(score_change, 2)

        # apply change values
        session.score += score_change
        session.health += health_change
        # rounding prevents floating-point precision issues like score_change being output as '-14.399999999999999'
        session.score = round(session.score, 2)
        session.health = round(session.health, 2)
        # score and health values must be from 0 to 100 only
        session.score = max(0, session.score)
        session.score = min(session.score, 100)
        # health values must be from 0 to 100 only
        session.health = max(0, session.health)
        session.health = min(session.health, 100)

        # update wrong count if answer was not good
        if outcome != 'good':
            session.wrong_count += 1

        # mark question as answered
        question.is_answered = True
        question.selected_option_id = selected_option_id

        # save changes for below checks
        question.save()
        session.save()

        all_questions_complete = False
        scenario_failed = False

        # check if health is 0, means scenario failed
        if session.health <= 0:
            scenario_failed = True
            session.status = 'failed'
            session.completed_at = timezone.now()

        if not scenario_failed:
            # check for any questions left within that stage
            this_stage_questions_left = QuestionRun.objects.filter(
                stage_name = stage.stage_name,
                is_answered = False
            ).exists()

            # no question left, go to next question and activate the corresponding stage
            if not this_stage_questions_left:
                stage.status = 'done'
                # find the next question
                next_question = QuestionRun.objects.filter(
                    session = session,
                    id__gt = question.id
                ).order_by('id').first()

                # if there is a next question, find the corresponding stage and set it to active
                if next_question:
                    stage_to_activate = StageRun.objects.get(
                        session = session,
                        stage_name = next_question.stage_name,
                    )
                    stage_to_activate.status = 'active'
                    stage_to_activate.save()
                # if no more questions, set scenario as completed
                else:
                    all_questions_complete = True
                    session = question.session
                    session.status = 'completed'
                    session.completed_at = timezone.now()

        # save changes made from checks (if any) to database
        question.save()
        session.save()
        stage.save()

        return {
            'outcome': outcome,
            'score_change': score_change,
            'health_change': health_change,
            'new_score': session.score,
            'new_health': session.health,
            'wrong_count': session.wrong_count,
            'all_questions_complete': all_questions_complete,
            'scenario_failed': scenario_failed,
        }

