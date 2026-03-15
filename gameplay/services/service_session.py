import requests, json

from django.db import transaction

from ..models import (GameSession,
                      StageRun,
                      QuestionRun,
                      Playbook)

@transaction.atomic
def create_session(user, incident_type, difficulty):

    session = GameSession.objects.create(
        user = user,
        incident_type = incident_type,
        difficulty = difficulty,
        status = 'in progress',

        scenario_json = generate_ai_scenario(
            incident_type = incident_type,
            difficulty = difficulty,
        )
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

def generate_ai_scenario(incident_type, difficulty):
    prompt = f"""
        Generate a cyber incident training scenario.
    
        Incident type: {incident_type}
        Difficulty: {difficulty}
    
        Return ONLY valid JSON.
    
        Format:
        {{
          "scenario_title": "",
          "scenario_brief": "",
          "injects": [
            {{"stage":"Detect","text":""}},
            {{"stage":"Analyse","text":""}},
            {{"stage":"Remediation","text":""}}
          ]
        }}
    """.strip()

    try:
        response = requests.post(
            url = 'http://localhost:11434/api/generate/',
            json = {
                'model': 'llama3:latest',
                'prompt': prompt,
                'stream': False
            },
            timeout = 60,
        )

        response.raise_for_status()
        data = response.json()
        raw = data.get('response', '').strip()

        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found in AI response.")

        json_text = raw[start:end]

        return json.loads(json_text)

    except Exception as e:
        print(f"[AI scenario fallback triggered] {e}")
        return {
            "scenario_title": f"{incident_type.title()} Incident",
            "scenario_brief": f"A {difficulty} level {incident_type} incident has been detected.",
            "injects": [
                {"phase": "Detect", "text": "Initial suspicious activity reported."},
                {"phase": "Analyse", "text": "Security team begins investigation."},
                {"phase": "Remediation", "text": "Containment actions initiated."},
            ],
        }
