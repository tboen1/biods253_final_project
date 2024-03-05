import numpy as np
import pandas as pd
from tqdm import tqdm

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
    
    Args:
        - answer: five letter word
        - guess: five letter word
        
    Returns:
        - color: five letter string representing sequence of G,Y,X outputs
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

def get_color_distribution(guess: str, possible_answers: set,
                           show_progress: bool = True):
    '''
    Given a guess and a set of possible answers, 
    computes the distribution of possible color outputs
    as a dictionary. 
    
    Args:
        - guess. Word to guess
        - possible_answers. set of potential answers
        
    Returns:
        - dist. Dictionary with keys outputs and values
                list of words that could've generated that output
    '''
    
    dist = {}
    
    for answer in tqdm(possible_answers, total = len(possible_answers),
                       disable = not show_progress):
        output = guess2color(answer = answer, guess = guess)
        
        if output in dist.keys():
            dist[output].append(answer)
        
        else:
            dist[output] = [answer]
            
    return dist

def get_expected_information(guesses: set, answers: set, show_progress = True):
    '''
    Given a set of guesses and a set of possible answers, 
    computes the expected information of each guess. 
    
    That is, for a given guess g, it's expected information E_g[I]
    is given by: 
    
    E_g[I] = - \Sum_x p(x) \log_2(p(x))
    
    Where x indicates a color output, and p(x) indicates 
    the probability of that color output occuring given the 
    set of possible answers. 
    
    Args:
        - guesses: set of guess words
        - answers: set of possible answer words
        
    Returns: 
        - guess_information: dictionary with keys guesses andd 
                             values expected information for that guess
    '''
    
    guess_information = {}
    
    for g in tqdm(guesses, total = len(guesses), disable = not show_progress):
        color_dist = get_color_distribution(guess = g, 
                                            possible_answers = answers, 
                                            show_progress = False)

        num_matches = np.asarray([len(color_dist[key]) for 
                                  key in color_dist.keys()])
        
        p_vals = num_matches/np.sum(num_matches)

        expected_information = -np.sum(p_vals * np.log2(p_vals))
        
        guess_information[g] = expected_information
        
    return guess_information
