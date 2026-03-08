from django.shortcuts import render
from rest_framework.response import Response

def get_scenario(request):
    scene = request.GET.get('scene')
    difficulty = request.GET.get('difficulty')

    return Response({'scene': scene, 'difficulty': difficulty})

