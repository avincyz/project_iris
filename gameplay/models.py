from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('tech', 'Technical'),
        ('nontech', 'Non-Technical'),
    )

    role = models.CharField(max_length = 20, choices = ROLE_CHOICES, default = 'nontech')

# represents a full simulation run
class GameSession(models.Model):

    INCIDENT_TYPE_CHOICES = [
        ('phishing','Phishing'),
        ('ransomware', 'Ransomware'),
        ('malware', 'Malware'),
        ('data_loss','Data Loss'),
        ('denial_of_service','DoS'),
    ]

    STATUS_CHOICES = [
        ('in progress', 'In Progress'),
        ('paused', 'Paused'),
        ('completed', 'Completed'), # when all questions are complete
        ('failed', 'Failed'), # fails if health reaches 0
        ('abandoned', 'Abandoned'), # user quits
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    incident_type = (models.CharField(
        max_length = 50,
        choices = INCIDENT_TYPE_CHOICES)
    )

    difficulty = models.IntegerField()

    status = models.CharField(
        max_length = 20,
        choices = STATUS_CHOICES,
        default = 'in progress',
    )

    score = models.IntegerField(default = 0)
    wrong_count = models.IntegerField(default = 0)
    pressure_level = models.IntegerField(default = 0)

    health = models.IntegerField(default = 100)

    created_at = models.DateTimeField(auto_now_add = True)
    completed_at = models.DateTimeField(null = True, blank = True)

    def __str__(self):
        return f'Session {self.id} - {self.incident_type} - {self.status}'

# this represents the scenario structure
class ScenarioSnapshot(models.Model):

    session = models.ForeignKey(
        GameSession,
        on_delete = models.CASCADE,
        related_name = 'snapshots'
    )

    seed = models.IntegerField(default = 0)

    scenario_json = models.JSONField()
    generated_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'Scenario Snapshot for Session {self.session.id}'

# this represents the stages within the scenario
class StageRun(models.Model):

    STAGE_TYPE_CHOICES = [
        ('prepare', 'Prepare'),
        ('detect', 'Detect'),
        ('analyse', 'Analyse'),
        ('remediate', 'Remediate'),
        ('post_incident', 'Post Incident'),
    ]

    STATUS_CHOICES = [
        ('locked', 'Locked'),
        ('active', 'Active'),
        ('done', 'Done'),
    ]

    session = models.ForeignKey(
        GameSession,
        on_delete=models.CASCADE,
        related_name = 'stages'
    )

    stage_name = models.CharField(
        max_length = 20,
        choices = STAGE_TYPE_CHOICES
    )

    status = models.CharField(
        max_length = 10,
        choices = STATUS_CHOICES,
        default = 'locked'
    )

    order_index = models.IntegerField(default = 0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'stage_name'],
                name='unique_stage_name_per_session',
            )
        ]

    def __str__(self):
        return f'{self.stage_name} - Session {self.session.id}'

# this stores question snapshots within a session
class QuestionRun(models.Model):

    session = models.ForeignKey(
        GameSession,
        on_delete = models.CASCADE,
        related_name = 'questions'
    )

    stage_name = models.CharField(max_length = 20)

    question_uid = models.CharField(max_length = 100)
    question_text = models.TextField()

    options_json = models.JSONField()

    time_limit_seconds = models.IntegerField(default = 20)

    order_index = models.IntegerField(default = 0)

    is_answered = models.BooleanField(default = False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['session', 'question_uid'],
                name = 'unique_question_uid_per_session',
            )
        ]

    def __str__(self):
        return self.question_uid

# this stores the user's answer for each question
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
        return f'Answer for Question {self.question_id} - {self.selected_option_id}'

class DebriefSnapshot(models.Model):
    session = models.OneToOneField(
        GameSession,
        on_delete = models.CASCADE,
        related_name = 'debrief'
    )

    debrief_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'Debrief for Session {self.session.id}'