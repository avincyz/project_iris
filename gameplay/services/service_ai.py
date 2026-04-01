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
        Generate a short paragraph of a cyber incident update with the following details. It should not be more than 25 words long.
    
        Topic: {incident_type}
        Severity: {severity}
    
        Return ONLY valid JSON. Use the format below.
    
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
        You are generating a cybersecurity scenario injection question.

        Incident type: {incident_type}
        Severity: {severity}
        
        Return ONLY valid JSON.
        Do not include markdown fences.
        Do not include explanations.
        
        Format:
        {{
          "question_text": "short scenario question",
          "options": [
            {{
              "option_uid": "A",
              "option_text": "good response",
              "outcome": "good"
            }},
            {{
              "option_uid": "B",
              "option_text": "bad response",
              "outcome": "bad"
            }}
          ]
        }}
        
        Rules:
        - The injection must be phrased as a question.
        - There must be exactly 2 answers.
        - Answer A must be the answer with a good outcome.
        - Answer B must be the answer with a bad outcome.
        - Keep it realistic and concise.
        - Keep the question under 50 words.
        - Match the incident type and severity.
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

        return parsed_text

    except Exception as e:
        print(f"[AI scenario fallback triggered] {e}")
        return {
            "question_text": f"A {severity} {incident_type} escalation is developing. What should the team do next?",
            "options": [
                {
                    "option_uid": "A",
                    "option_text": "Investigate and respond immediately",
                    "outcome": "good",
                },
                {
                    "option_uid": "B",
                    "option_text": "Delay action and hope it resolves itself",
                    "outcome": "bad",
                },
            ],
        }

def generate_ai_feedback(session):
    questions_answered_wrong = QuestionRun.objects.filter(
        session = session,
        answer_is_correct = False,
    )

    if not questions_answered_wrong and session.status == 'completed':
        return "Well done! You completed the scenario without any incorrect answers."

    if not questions_answered_wrong and session.status == 'abandoned':
        return (
            'You answered all questions correctly.\n'
            'However, the scenario was abandoned before completion.\n'
            'Thus, performance cannot be accurately accessed.\n'
            'Please complete a scenario without abandoning for a full debrief.\n'
            'It is recommended to review all relevant verification, escalation and response procedures before attempting again.'
        )

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

    Generate a generalised debrief for a tabletop training session.

    Session status: {session.status}
    Topic: {session.incident_type}
    Wrong count: {session.wrong_count}
    
    The debrief must:
    - be concise
    - be generalised, not overly detailed
    - include overall performance
    - include key weakness areas
    - include recommended next steps
    - if the session was abandoned, mention that it was incomplete
    
    Return plain text with short bullet points.

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
        return data.get('response', '').strip()

    except Exception as e:
        print(f"[AI feedback fallback triggered] {e}")
        fallback_feedback = []

        for item in questions_answered_wrong_data:
            fallback_feedback.append(
                f'- Question: {item["question"]}\n'
                f'  Your selected option: {item["selected_wrong_option"]}\n'
                f'  Correct option: {item["correct_option"]}\n'
            )

        fallback_feedback.append("General Debrief:")
        if session.status == "abandoned":
            fallback_feedback.append("- Session was abandoned before completion.")

        fallback_feedback.append(f"- Topic: {session.incident_type}")
        fallback_feedback.append(f"- Incorrect answers recorded: {session.wrong_count}")

        if session.wrong_count > 0:
            fallback_feedback.append("- Incident recognition and response decision-making was lacking.")
            fallback_feedback.append("- Please review incorrect decisions and try the scenario again.")
        else:
            fallback_feedback.append("- Well done! All questions were answered correctly.")

        return '\n'.join(fallback_feedback)