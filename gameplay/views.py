from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import GameSession, DebriefSnapshot
from .serializers import GameSessionStartSerializer, GenerateQuestionsSerializer, AnswerQuestionSerializer
from .services.service_session import create_session, get_session_state
from .services.service_question import generate_questions
from .services.service_answer import process_answer
from .services.service_debrief import generate_debrief

# view to start a new session
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def session_start_view(request):
    serializer = GameSessionStartSerializer(data = request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    session = create_session(
        user = request.user,
        incident_type = serializer.validated_data['incident_type'],
        difficulty = serializer.validated_data['difficulty'],
    )

    return Response({
        'session_id' : session.id,
        'status': session.status,
    })

# view to generate new questions
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_questions_view(request, stage_name):

    serializer = GenerateQuestionsSerializer(data = request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    questions = generate_questions(
        session_id = data['session_id'],
        stage_name = stage_name
    )

    response_data = []

    for question in questions:
        response_data.append({
            'id' : question.id,
            'question_uid' : question.question_uid,
            'question_text' : question.question_text,
            'options' : question.options_json,
            'time_limit' : question.time_limit_seconds,
        })

    return Response(response_data)

# view for when user answers a question
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def answer_question_view(request, question_id):
    serializer = AnswerQuestionSerializer(data = request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        result = process_answer(
            session_id = data['session_id'],
            question_id = question_id,
            selected_option_id = data['selected_option_id'],
        )

        return Response(result)

    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# view to generate debrief after the scenario ends
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_debrief_view(request, session_id):
    try:
        session = GameSession.objects.get(id = session_id)
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'Session does not exist'},
            status=status.HTTP_404_NOT_FOUND
        )

    if hasattr(session, 'debrief'):
        return Response({
            'message': 'There is already a debrief for this session',
            'debrief': session.debrief.debrief_json
        })

    debrief_data = generate_debrief(session)

    debrief_snapshot = DebriefSnapshot.objects.create(
        session = session,
        debrief_json = debrief_data
    )

    return Response({
        'message': 'Debrief Generated',
        'debrief': debrief_snapshot.debrief_json
    })

# view to pause the session
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pause_session(request, session_id):
    try:
        session = GameSession.objects.get(id = session_id)
    except GameSession.DoesNotExist:
        return Response({'error': 'Session does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if session.status != 'in progress':
        return Response(
            {'error': 'Only sessions currently in progress can be paused',
             'session_id': session.id,
             'status': session.status},
            status=status.HTTP_400_BAD_REQUEST
        )

    session.status = 'paused'
    session.save()

    return Response({
        'message': 'Session paused',
        'session_id': session.id
    })

# view to resume a paused session
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resume_session(request, session_id):
    try:
        session = GameSession.objects.get(id = session_id)
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'Session does not exist'}, status=status.HTTP_404_NOT_FOUND
        )

    # check if session is already done (cannot be resumed)
    if session.status not in ['paused', 'in progress']:
        return Response(
            {'error': 'Session cannot be resumed'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # get existing session state, check if it exists
    session_state = get_session_state(session)
    if not session_state:
        return Response(
            {'error': 'No session state found',},
            status=status.HTTP_400_BAD_REQUEST
        )

    session.status = 'in progress'
    session.save()

    return Response({
        'message': 'Session resumed',
        'session_id': session.id,
        'status': session.status,
        **session_state
    })

# view for if the user abandons the scenario
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def abandon_session(request, session_id):
    try:
        session = GameSession.objects.get(id = session_id)
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'Session does not exist'}, status=status.HTTP_404_NOT_FOUND
        )

    if session.status in ['completed', 'failed', 'abandoned']:
        return Response(
            {'error': 'Scenario is already over'},
            status=status.HTTP_400_BAD_REQUEST
        )

    session.status = 'abandoned'
    session.completed_at = timezone.now()
    session.save()

    return Response({
        'message': 'Session abandoned',
    })

# view to list a user's active sessions
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_active_sessions(request):
    sessions = GameSession.objects.filter(
        user = request.user,
        status__in = ['in progress', 'paused']
    ).order_by('-created_at')

    data = [
        {
            'id' : s.id,
            'incident_type': s.incident_type,
            'status': s.status,
            'score': s.score,
            'health': s.health,
        }
        for s in sessions
    ]

    return Response(data)