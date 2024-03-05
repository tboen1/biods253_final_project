import numpy as np
import pandas as pd

def load_words(fp: str) -> set:
    '''
    Loads list of wordle words
    
    Params:
        fp: file path to wordle word list
    '''
    
    with open(fp) as word_file:
        valid_words = set(word_file.read().split())

    return valid_words

def guess2color(answer: str, guess: str):
    '''
    Grades wordle guess, producing colored output
    according to the wordle rules
    
    Rules: 
        - Green (G): correct letter and position
        - Yellow (Y): correct letter but incorrect
        - Gray (X): not in word
    
    Note: 
    there is a little ambiguity in the rules concerning duplicate letters 
    and what their colors are, but this function attempts to replicate the 
    behavior in the official NYT application, and marks any duplicate letters 
    as gray and not yellow. 
    
    Example:
        - answer: CHILD
        - guess:  COUCH
        - color:  GXXXY
        
    Note that the second C in COUCH is marked as gray and not yellow. 
    '''
        
    assert len(answer) == 5, "answer must be a 5 letter word!"
    assert len(guess) == 5, "answer must be a 5 letter word!"
    
    color = [''] * len(answer)
    misplaced = []

    # Check for correct letters in the correct position
    for i in range(len(answer)):
        if guess[i] == answer[i]:
            color[i] = 'G'  # Green block
        else:
            misplaced.append(answer[i])

    # Check for correct letters in the wrong position
    for i in range(len(answer)):
        if color[i] != 'G':
            if guess[i] in misplaced:
                misplaced.remove(guess[i])
                color[i] = 'Y'  # Yellow block
            else:
                color[i] = 'X'  # Grey block

    return ''.join(color)


