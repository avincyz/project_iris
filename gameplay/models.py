from django.db import models
from django.contrib.auth.models import AbstractUser

from .config.choices import (USER_ROLE_CHOICES,
                             INCIDENT_TYPE_CHOICES,
                             SESSION_STATUS_CHOICES,
                             STAGE_TYPE_CHOICES,
                             STAGE_STATUS_CHOICES,
                             DIFFICULTY_CHOICES)

# a single user of the app
class User(AbstractUser):
    role = models.CharField(max_length = 20, choices = USER_ROLE_CHOICES, default = 'nontech')

# a full simulation run
class GameSession(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    incident_type = models.CharField(
        max_length = 50,
        choices = INCIDENT_TYPE_CHOICES
    )

    difficulty = models.CharField(
        max_length = 10,
        choices = DIFFICULTY_CHOICES
    )

    status = models.CharField(
        max_length = 20,
        choices = SESSION_STATUS_CHOICES,
        default = 'in progress',
    )

    scenario_json = models.JSONField()

    score = models.IntegerField(default = 0)
    wrong_count = models.IntegerField(default = 0)
    pressure_level = models.IntegerField(default = 0)

    health = models.IntegerField(default = 100)

    created_at = models.DateTimeField(auto_now_add = True)
    completed_at = models.DateTimeField(null = True, blank = True)

    def __str__(self):
        return f'Session {self.id} - {self.incident_type} - {self.status}'

# a playbook which the AI will reference to generate the scenario
class Playbook(models.Model):
    slug = models.SlugField(max_length = 50)
    difficulty = models.CharField(max_length = 10, choices = DIFFICULTY_CHOICES)
    version = models.PositiveIntegerField(default = 1)

    class Meta:
        unique_together = ('slug', 'difficulty', 'version')

    def __str__(self):
        return f'{self.slug} ({self.difficulty}) v{self.version}'

# a single question snapshot within a session
# the question and options that will be displayed are taken from the GeneratedQuestion and GeneratedOption objects
class QuestionRun(models.Model):

    session = models.ForeignKey(
        GameSession,
        on_delete = models.CASCADE,
        related_name = 'questions'
    )

    stage_name = models.CharField(max_length = 50)

    question_uid = models.CharField(max_length = 100)
    question_text = models.TextField()

    options_json = models.JSONField()
    selected_option_id = models.CharField(max_length = 10)

    time_limit_seconds = models.IntegerField(default = 20)

    order_index = models.IntegerField(default = 0)

    is_answered = models.BooleanField(default = False)
    answer_is_correct = models.BooleanField(default = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['session', 'question_uid'],
                name = 'unique_question_uid_per_session',
            )
        ]

    def __str__(self):
        return self.question_uid


# a stage within the scenario
# one scenario will typically consist of five pages
class StageRun(models.Model):
    session = models.ForeignKey(
        GameSession,
        on_delete = models.CASCADE,
        related_name = 'stages'
    )

    stage_name = models.CharField(
        max_length = 50,
        choices = STAGE_TYPE_CHOICES
    )

    status = models.CharField(
        max_length = 10,
        choices = STAGE_STATUS_CHOICES,
        default = 'locked'
    )

    order_index = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['session', 'stage_name'],
                name = 'unique_stage_name_per_session',
            )
        ]

    def __str__(self):
        return f'{self.stage_name} - Session {self.session.id}'

# a single ai-generated question within a scenario
class GeneratedQuestion(models.Model):
    playbook = models.ForeignKey(
        Playbook,
        on_delete = models.CASCADE,
        related_name = 'playbook'
    )
    question_id = models.CharField(max_length = 120, unique = True)
    stage_name = models.CharField(max_length = 20, choices = STAGE_TYPE_CHOICES)
    prompt = models.TextField()
    is_active = models.BooleanField(default = True)

    class Meta:
        indexes = [
            models.Index(fields = ['playbook', 'stage_name']),
            models.Index(fields = ['id']),
        ]

    def __str__(self):
        return f'{self.id}'

# a single option for an ai-generated question
class Option(models.Model):
    question = models.ForeignKey(
        GeneratedQuestion,
        on_delete = models.CASCADE,
        related_name = 'options'
    )
    option_uid = models.CharField(max_length = 1) # A/B/C
    option_text = models.TextField()
    outcome = models.CharField(max_length = 10)

    class Meta:
        unique_together = ('question', 'option_uid')

    def __str__(self):
        return f'{self.question.id} - Option {self.option_uid}'

# the user's answer for each question
class Answer(models.Model):

    question = models.ForeignKey(
        QuestionRun,
        on_delete = models.CASCADE,
        related_name = 'answers'
    )

    selected_option_id = models.CharField(max_length = 10)
    submitted_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['question'],
                name = 'one_answer_per_question'
            )
        ]

    def __str__(self):
        return f'Answer for Question {self.question.question_uid} - {self.selected_option_id}'

# the debrief shown after a scenario has ended
class DebriefSnapshot(models.Model):
    session = models.OneToOneField(
        GameSession,
        on_delete = models.CASCADE,
        related_name = 'debrief'
    )

    debrief_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'Debrief for Session {self.session.id}'

