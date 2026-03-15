from django.contrib import admin
from . import models

admin.site.register(models.GameSession)
admin.site.register(models.StageRun)
admin.site.register(models.QuestionRun)
admin.site.register(models.Answer)
admin.site.register(models.DebriefSnapshot)

admin.site.register(models.Playbook)
admin.site.register(models.GeneratedQuestion)
admin.site.register(models.Option)