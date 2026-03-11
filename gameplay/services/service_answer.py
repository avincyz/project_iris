from django.db import transaction
from django.utils import timezone

from ..config.score_sheet import OUTCOME_SCORES, OUTCOME_HEALTH_CHANGES, DIFFICULTY_MODIFIER
from ..models import GameSession, QuestionRun, StageRun

def process_answer(session_id, question_id, selected_option_id):

    with transaction.atomic():
        session = GameSession.objects.get(id = session_id)
        question = QuestionRun.objects.get(
            session = session,
            id = question_id
        )
        stage_name = StageRun.objects.get(
            session = question.session,
            stage_name = question.stage_name,
        )
        difficulty = session.difficulty
        diff_modifier = DIFFICULTY_MODIFIER.get(difficulty, 1.0)

        # check if scenario is already finished
        if session.status in ['completed', 'failed', 'abandoned']:
            raise ValueError('Scenario is already over')

        # check if the stage is active
        if stage_name.status != 'active':
            raise ValueError('Stage is not active')

        # check if question has been answered (in cases like answers being spammed)
        if question.is_answered:
            raise ValueError('Question has already been answered')

        options = question.options_json
        selected_option = None

        for option in options:
            if selected_option_id == option['id']:
                selected_option = option
                break

        if not selected_option:
            raise ValueError('Option not found')

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

        stage_complete = False
        all_stages_complete = False
        scenario_failed = False

        # check if health is 0, means scenario failed
        if session.health <= 0:
            scenario_failed = True
            session.status = 'failed'
            session.completed_at = timezone.now()

        if not scenario_failed:
            # check for any questions left
            questions_left = QuestionRun.objects.filter(
                stage_name = question.stage_name,
                is_answered = False
            ).exists()

            # no question left, go to next stage
            if not questions_left:
                # mark current stage as complete
                stage_complete = True
                stage_name.status = 'done'
                stage_name.completed_at = timezone.now()

                # check if there is a next stage
                next_stage = StageRun.objects.filter(
                    session = session,
                    order_index__gt = stage_name.order_index,
                ).order_by('order_index').first()

                # if next stage exists, set it to active
                if next_stage:
                    next_stage.status = 'active'
                    next_stage.save()
                # if no more stages, mark scenario as complete
                else:
                    all_stages_complete = True
                    session = question.session
                    session.status = 'completed'
                    session.completed_at = timezone.now()

        # save changes made from checks (if any) to database
        question.save()
        session.save()
        stage_name.save()

        return {
            'outcome': outcome,
            'score_change': score_change,
            'health_change': health_change,
            'new_score': session.score,
            'new_health': session.health,
            'wrong_count': session.wrong_count,
            'current_stage_complete': stage_complete,
            'all_stages_complete': all_stages_complete,
            'scenario_failed': scenario_failed,
        }

