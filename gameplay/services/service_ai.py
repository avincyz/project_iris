import requests, json

from gameplay.models import QuestionRun


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

def generate_ai_inject(incident_type, severity):
    prompt = f"""
        Generate a short cyber incident update.
    
        Topic: {incident_type}
        Severity: {severity}
    
        Return ONLY valid JSON.
    
        Format:
        {{ "inject": "" }}
    """.strip()

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:latest",
                "prompt": prompt,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        raw = data.get('response', '').strip()

        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found in AI response.")

        json_text = raw[start:end]
        parsed_text = json.loads(json_text)

        return parsed_text.get("inject")

    except Exception as e:
        print(f"[AI scenario fallback triggered] {e}")
        return 'Inject message generated'

def generate_ai_crisis_event(incident_type, severity):
    prompt = f"""
        You are generating a sudden cyber crisis escalation event.
    
        Incident type: {incident_type}
        Severity: {severity}
    
        Return ONLY valid JSON.
        Do not include markdown fences.
        Do not include explanations.
    
        Format:
        {{"crisis_event": "short unexpected escalation message"}}
    
        Rules:
        - Keep it realistic
        - Make it feel urgent
        - Keep it under 25 words
        - The event must match the incident type
    """.strip()

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:latest",
                "prompt": prompt,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()

        data = response.json()
        raw = data.get('response', '').strip()

        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found in AI response.")

        json_text = raw[start:end]
        parsed_text = json.loads(json_text)

        return parsed_text.get("crisis_event")

    except Exception as e:
        print(f"[AI scenario fallback triggered] {e}")
        return 'Crisis event generated'

def generate_ai_feedback(session):
    questions_answered_wrong = QuestionRun.objects.filter(
        session = session,
        answer_is_correct = False,
    )

    if not questions_answered_wrong:
        return "Well done! You completed the scenario without any incorrect answers."

    # for testing
    # print(questions_answered_wrong)

    questions_answered_wrong_data = []

    for q in questions_answered_wrong:
        correct_option = None
        selected_option = None

        for option in q.options_json:
            if option.get('outcome') == 'good':
                correct_option = option.get('option_text')
            if option.get('option_uid') == q.selected_option_id:
                selected_option = option.get('option_text')

        questions_answered_wrong_data.append({
            'question': q.question_text,
            'selected_wrong_option': selected_option,
            'correct_option': correct_option,
        })

    # for testing
    print(questions_answered_wrong_data)

    prompt = f"""
    You are a cybersecurity training instructor.

    Generate learning feedback for a player who answered questions incorrectly.

    Explain briefly:
    - why their answer was wrong
    - what the correct response is
    - what best practice should be

    Return bullet points.

    Incorrect answers:
    {json.dumps(questions_answered_wrong_data, indent = 2)}
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:latest",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data.get('response', '')

    except Exception as e:
        print(f"[AI feedback fallback triggered] {e}")
        fallback_feedback = []
        for item in questions_answered_wrong_data:
            fallback_feedback.append(
                f'- Question: {item["question"]}\n'
                f'  Your selected option: {item["selected_wrong_option"]}\n'
                f'  Correct option: {item["correct_option"]}\n'
            )
        return '\n'.join(fallback_feedback)