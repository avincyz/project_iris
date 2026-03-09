from ..models import StageRun

# TODO: replace this with function to AI-generate the debrief
def generate_debrief(session):
    stages = StageRun.objects.filter(
        session = session
    ).order_by('order_index')

    stage_results = []

    for stage in stages:
        stage_results.append({
            'stage_name': stage.stage_name,
            'status': stage.status,
        })

    debrief = {
        'summary': 'This is where the summary will go.',
        'status': session.status,
        'final_score': session.score,
        'wrong_answers': session.wrong_count,
        'stages': stage_results,
        'strengths': [
            "Placeholder Strengths Text"
        ],
        'weaknesses': [
            "Placeholder Weaknesses Text"
        ],
        'recommendations': [
            "Placeholder Recommendations Text"
        ],
    }

    return debrief