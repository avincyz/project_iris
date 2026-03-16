OUTCOME_HEALTH_CHANGES = {
    'good': 3,
    'risky': -5,
    'bad': -10,
    'timeout': -20
}

OUTCOME_SCORE_CHANGES = {
    'good': 10,
    'risky': 2,
    'bad': -12,
    'timeout': -20
}

PRESSURE_CHANGES = {
    'good': -5,
    'risky': 10,
    'bad': 20,
    'timeout': 40
}

# note that this is a list of tuples instead of a dictionary list because it has to account for a range of values
SEVERITY_CHOICES = [
    (80, 'critical'),
    (60, 'high'),
    (40, 'medium'),
    (0, 'low'),
]

# note: this modifier should only affect health and score penalties
DIFFICULTY_MODIFIER = {
    'easy': 0.8,     # easy
    'medium': 1,       # medium
    'hard': 1.2,     # critical
}

