import requests, json

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