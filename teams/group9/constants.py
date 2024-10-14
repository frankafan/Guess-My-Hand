# Use to get card value with order 2 to A
CARD_VAL = {
    '2' : 0,
    '3' : 1,
    '4' : 2,
    '5' : 3,
    '6' : 4,
    '7' : 5,
    '8' : 6,
    '9' : 7,
    '10' : 8,
    'J' : 9,
    'Q' : 10,
    'K' : 11,
    'A' : 12,
}
# Use to shift card value
CARD_SHIFT = {
    '2' : '3',
    '3' : '4',
    '4' : '5',
    '5' : '6',
    '6' : '7',
    '7' : '8',
    '8' : '9',
    '9' : '10',
    '10' : 'J',
    'J' : 'Q',
    'Q' : 'K',
    'K' : 'A',
    'A' : 'A',
}
# Use to get suit value
SUIT_VAL = {
    'Spades' : 0,
    'Clubs' : 1,
    'Hearts' : 2,
    'Diamonds' : 3,
}

# Use to get teammate of current player
TEAMMATE = {
    "North" : "South",
    "South" : "North",
    "East" : "West",
    "West" : "East",
}

# teammate_max = ''
# PLAYER_GUESSES = {
#     'North' : [],
#     'East' : [],
#     'South' : [],
#     'West' : []
# }

# EXPOSED_CARDS = []