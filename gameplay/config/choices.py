USER_ROLE_CHOICES = (
    ('tech', 'Technical'),
    ('nontech', 'Non-Technical'),
)

INCIDENT_TYPE_CHOICES = [
    ('phishing','Phishing'),
    ('ransomware', 'Ransomware'),
    ('malware', 'Malware'),
    ('data_loss','Data Loss'),
    ('denial_of_service','DoS'),
]

SESSION_STATUS_CHOICES = [
    ('in progress', 'In Progress'),
    ('paused', 'Paused'),
    ('completed', 'Completed'), # when all questions are complete
    ('failed', 'Failed'), # fails if health reaches 0
    ('abandoned', 'Abandoned'), # user quits
]

STAGE_TYPE_CHOICES = [
    ('prepare', 'Prepare'),
    ('detect', 'Detect'),
    ('analyse', 'Analyse'),
    ('remediate', 'Remediation'),
    ('post_incident', 'Post-Incident'),
]

STAGE_STATUS_CHOICES = [
    ('locked', 'Locked'),
    ('active', 'Active'),
    ('done', 'Done'),
]

DIFFICULTY_CHOICES = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
]