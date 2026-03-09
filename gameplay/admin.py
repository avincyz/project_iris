from django.contrib import admin
from . import models

admin.site.register(models.GameSession)
admin.site.register(models.StageRun)
admin.site.register(models.QuestionRun)
admin.site.register(models.Answer)
admin.site.register(models.ScenarioSnapshot)
admin.site.register(models.DebriefSnapshot)