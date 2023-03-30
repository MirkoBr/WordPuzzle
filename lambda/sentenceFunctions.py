import numpy as np
import random
import json

ALL_SENTENCES = {
    "en-US": {
        "file": "./documents/words_en.txt"
    },
    "de-DE": {
        "file": "./documents/words_de.txt"
    }
}

def load_sentence_library(locale):
    current_file = ALL_SENTENCES[locale]['file']
    setences = []
    current_file = open(current_file)
    setences = current_file.read()
    setences = setences.split('\n')
    return setences

def get_random_sentence_remove_past(sentence_library, past_sentences):
    keep_sentences = []
    for d in sentence_library:
        if d not in past_sentences:
            keep_sentences.append(d)
    if len(keep_sentences) == 0:
        current_sentence = None
        return current_sentence
    current_sentence = random.choice(keep_sentences)
    return current_sentence

def tokenize_sentence(input_sentence):
    """splits sentence into words as list"""
    current_sentence = input_sentence.upper()
    current_sentence = current_sentence.replace('.','')
    current_sentence = current_sentence.replace(',','')
    current_words = current_sentence.split()
    return current_words

def nw(x, y, match = 1, mismatch = 1, gap = 1):
    """needlman wunsch alignment"""
    nx = len(x)
    ny = len(y)
    # Optimal score at each possible pair of characters.
    F = np.zeros((nx + 1, ny + 1))
    F[:,0] = np.linspace(0, -nx * gap, nx + 1)
    F[0,:] = np.linspace(0, -ny * gap, ny + 1)
    # Pointers to trace through an optimal aligment.
    P = np.zeros((nx + 1, ny + 1))
    P[:,0] = 3
    P[0,:] = 4
    # Temporary scores.
    t = np.zeros(3)
    for i in range(nx):
        for j in range(ny):
            if x[i] == y[j]:
                t[0] = F[i,j] + match
            else:
                t[0] = F[i,j] - mismatch
            t[1] = F[i,j+1] - gap
            t[2] = F[i+1,j] - gap
            tmax = np.max(t)
            F[i+1,j+1] = tmax
            if t[0] == tmax:
                P[i+1,j+1] += 2
            if t[1] == tmax:
                P[i+1,j+1] += 3
            if t[2] == tmax:
                P[i+1,j+1] += 4
    # Trace through an optimal alignment.
    i = nx
    j = ny
    rx = []
    ry = []
    while i > 0 or j > 0:
        if P[i,j] in [2, 5, 6, 9]:
            rx.append(x[i-1])
            ry.append(y[j-1])
            i -= 1
            j -= 1
        elif P[i,j] in [3, 5, 7, 9]:
            rx.append(x[i-1])
            ry.append('-')
            i -= 1
        elif P[i,j] in [4, 6, 7, 9]:
            rx.append('-')
            ry.append(y[j-1])
            j -= 1
    # Reverse the strings.
    rx = ''.join(rx)[::-1]
    ry = ''.join(ry)[::-1]
    r = [rx, ry]
    return r

def tokenize_sentence(input_sentence):
    """"""
    current_sentence = input_sentence.upper()
    current_sentence = current_sentence.replace('.','')
    current_sentence = current_sentence.replace(',','')
    current_words = current_sentence.split()
    return current_words

'''
def check_answer(original_sentence, user_sentence):
    #checks how good sentences match
    original_sentence = original_sentence.upper()
    user_sentence = user_sentence.upper()
    alignment = nw(original_sentence, user_sentence)
    alignment_original = [*alignment[0]]
    alignment_guessed = [*alignment[1]]

    blanks = alignment_guessed.count(" ")
    splits = alignment_original.count("-")
    duplicated_words = (set(tokenize_sentence(original_sentence)) & set(tokenize_sentence(user_sentence)))
    duplicated_words = list(duplicated_words)
    duplicated_words_count = sum([len(i) for i in duplicated_words])

    position_matches = 0
    for i in range(len(alignment_original)):
        if alignment_original[i] == alignment_guessed[i]:
            position_matches = position_matches +1
    
    answer_points_possible = len(alignment_original) - blanks - splits
    answer_points = position_matches-blanks-duplicated_words_count
    if answer_points < 0:
        answer_points = 0
    return answer_points_possible, answer_points, alignment_original, alignment_guessed
'''

def check_answer(original_sentence, user_sentence):
    #checks how good sentences match
    original_sentence = original_sentence.upper()
    user_sentence = user_sentence.upper()
    alignment = nw(original_sentence, user_sentence)
    alignment_original = [*alignment[0]]
    alignment_guessed = [*alignment[1]]

    blanks = alignment_guessed.count(" ")
    splits = alignment_original.count("-")
    duplicated_words = (set(tokenize_sentence(original_sentence)) & set(tokenize_sentence(user_sentence)))
    duplicated_words = list(duplicated_words)
    duplicated_words_count = sum([len(i) for i in duplicated_words])

    position_matches = 0
    for i in range(len(alignment_original)):
        if alignment_original[i] == alignment_guessed[i]:
            position_matches = position_matches +1
    
    answer_points_possible = len(alignment_original) - blanks - splits
    answer_points = position_matches-blanks-duplicated_words_count

    pentalty_points = int(round(splits / 2, 0))

    pentalty_points = int(round((len(alignment_original) - answer_points) / 3, 0))
    answer_points_with_penalty = answer_points - pentalty_points

    if answer_points_with_penalty < 0:
        answer_points_with_penalty = 0

    return answer_points_possible, answer_points_with_penalty, alignment_original, alignment_guessed, pentalty_points, answer_points


def make_green(letter):
    #color_letter = f"<span color='green'>" + f"{letter}" + "</span>"
    color_letter = f"<span color='#8FC1D4'>" + f"{letter}" + "</span>"
    return color_letter

def make_red(letter):
    #color_letter = f"<span color='red'>" + f"{letter}" + "</span>"
    color_letter = f"<span color='#DEBA9D'>" + f"{letter}" + "</span>"
    return color_letter

def color_alignment(alignment_original, alignment_guessed):
    color_string = ""
    for i in range(len(alignment_original)):
        if alignment_original[i] == alignment_guessed[i]:
            color_string = color_string + make_green(alignment_original[i])
        if alignment_original[i] != alignment_guessed[i]:
            color_string = color_string + make_red(alignment_original[i])
    return color_string


