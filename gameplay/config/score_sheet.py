OUTCOME_HEALTH_CHANGES = {
    'good': 3,
    'risky': -5,
    'bad': -10,
    'timeout': -20
}

OUTCOME_SCORES = {
    'good': 10,
    'risky': 2,
    'bad': -12,
    'timeout': -20
}

# note: this modifier should only affect penalties
DIFFICULTY_MODIFIER = {
    1: 0.8,     # easy
    2: 1,       # medium
    3: 1.2,     # critical
}

