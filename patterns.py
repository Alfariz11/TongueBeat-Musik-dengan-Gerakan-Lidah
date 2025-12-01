# patterns.py
"""
Seven Drum Patterns for DrumMachine
Clean, professional, and compatible with the DrumMachine pattern structure.
"""
DRUM_PATTERNS = {
    # Pattern 0 — Modern Pop Groove
    0: {
        'kick': {0: 1.0, 4: 0.6, 8: 0.9, 12: 0.5},
        'snare': {5: 1.0, 13: 1.0},
        'hihat': {**{i: 0.45 for i in range(16)}},
        'hightom': {},
        'crashcymbal': {0: 0.8},
    },

    # Pattern 1 — Dark Trap Groove
    1: {
        'kick': {0: 1.0, 3: 0.7, 7: 0.9, 10: 0.55},
        'snare': {4: 1.0, 12: 1.0},
        'hihat': {2: 0.5, 6: 0.5, 10: 0.5, 14: 0.5},
        'hightom': {15: 0.4},
        'crashcymbal': {},
    },

    # Pattern 2 — Minimal Trap Beat
    2: {
        'kick': {0: 1.0, 8: 0.6},
        'snare': {4: 0.9, 12: 0.9},
        'hihat': {
            1: 0.35, 2: 0.55, 4: 0.35, 7: 0.6,
            9: 0.55, 12: 0.35, 15: 0.6
        },
        'hightom': {},
        'crashcymbal': {0: 0.9}
    },

    # Pattern 3 — Uptempo Breakbeat
    3: {
        'kick': {0: 1.0, 6: 0.8},
        'snare': {4: 1.0, 12: 1.0},
        'hihat': {
            **{i: 0.35 for i in range(16)},
            2: 0.55, 10: 0.55
        },
        'hightom': {7: 0.4, 15: 0.4},
        'crashcymbal': {0: 0.9}
    },

    # Pattern 4 — Bounce Groove
    4: {
        'kick': {
            0: 1.0, 2: 0.8, 4: 1.0, 6: 0.8,
            8: 1.0, 10: 0.8
        },
        'snare': {4: 0.9, 12: 0.9},
        'hihat': {2: 0.5, 6: 0.5, 10: 0.5, 14: 0.5},
        'hightom': {},
        'crashcymbal': {0: 0.75}
    },

    # Pattern 5 — Percussive Groove
    5: {
        'kick': {0: 1.0, 3: 0.9, 7: 0.75, 11: 0.8},
        'snare': {5: 1.0, 13: 1.0},
        'hihat': {**{i: 0.3 for i in range(16)}},
        'hightom': {9: 0.5},
        'crashcymbal': {}
    },

    # Pattern 6 — Dance/Pop Rhythm
    6: {
        'kick': {0: 1.0, 4: 1.0, 8: 1.0, 12: 1.0},
        'snare': {4: 1.0, 12: 1.0},
        'hihat': {
            2: 0.5, 6: 0.5, 10: 0.5, 14: 0.5,
            15: 0.7
        },
        'hightom': {7: 0.5},
        'crashcymbal': {0: 1.0}
    },
}

pattern_count = len(DRUM_PATTERNS)