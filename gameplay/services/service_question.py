import random
from ..models import GameSession, StageRun, QuestionRun

def generate_questions(session_id, stage_name):

    session = GameSession.objects.get(id = session_id)
    stage = StageRun.objects.get(
        session = session,
        stage_name = stage_name
    )

    if stage.status != 'active':
        raise ValueError('Stage is not active')

    # prevent duplicate generation
    existing = QuestionRun.objects.filter(
        session = session,
        stage_name = stage_name,
    )

    if existing.exists():
        return existing

    # TODO: replace below with AI-generated questions/scenarios
    placeholder_questions = [
        'How do you respond?',
        'Which is the best action to take?',
        'What step should you take next?',
        'What should you check first?',
        'Which strategy is the most appropriate?',
    ]

    num_questions = random.randint(1, 3)

    created_questions = []

    for i in range(num_questions):

        # TODO: replace with actual options from the AI-generated scenarios
        options = [
            {
                'id': 'A',
                'text': 'Good Option',
                'outcome': 'good'
            },
            {
                'id': 'B',
                'text': 'Risky Option',
                'outcome': 'risky'
            },
            {
                'id': 'C',
                'text': 'Bad Option',
                'outcome': 'bad'
            },
        ]

        random.shuffle(options)

        question = QuestionRun.objects.create(
            session = session,
            stage_name = stage_name,
            question_uid = f'{stage_name}_Question_{i + 1}',
            question_text = random.choice(placeholder_questions),
            options_json = options,

            time_limit_seconds = 20,
            order_index = i,
        )

        created_questions.append(question)

    return created_questions
