import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt

def load_words(fp: str) -> set:
    '''
    Loads list of all english words that contain only letters
    
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
    
    output = ["X"] * len(answer)

    for index, (guess_letter, target_letter) in enumerate(zip(guess, answer)):
        if guess_letter == target_letter:
            output[index] = "G"
            answer = answer.replace(guess_letter, "X", 1)
    
    for index, (guess_letter, target_letter) in enumerate(zip(guess, answer)):
        if guess_letter in answer and output[index] == "X":
            output[index] = "Y"
            answer = answer.replace(guess_letter, "X", 1)

    return ''.join(output)

def get_color_distribution(guess: str, possible_answers: set,
                           show_progress: bool = False):
    '''
    Given a guess and a set of possible answers, 
    computes the distribution of possible color outputs
    as a dictionary. 
    
    Args:
        - guess: Word to guess
        - possible_answers: set of potential answers
        - show_progress: display tqdm progress bar
        
    Returns:
        - dist: Dictionary with keys outputs and values
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

def get_expected_information(guesses: set, answers: set, 
                             return_sorted = True,
                             show_progress = False):
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
        - return_sorted: sort by decreasing information 
        - show_progress: display tqdm progress bar
        
    Returns: 
        - guess_information: dictionary with keys guesses andd 
                             values expected information for that guess
    '''
    
    guess_information = {}
    
    for g in tqdm(guesses, total = len(guesses), disable = not show_progress):
        color_dist = get_color_distribution(guess = g, 
                                            possible_answers = answers, 
                                            show_progress = False)

        num_matches = np.asarray([len(x) for x in list(color_dist.values())])
        
        p_vals = num_matches/np.sum(num_matches)

        expected_information = -np.sum(p_vals * np.log2(p_vals))
        
        guess_information[g] = expected_information
        
    if return_sorted:
        guess_information = dict(sorted(guess_information.items(), 
                                   key=lambda item: item[1], 
                                   reverse = True))
        
    return guess_information


def postprocessing_heuristic(guess_information, possible_answers):
    '''    
    In the case where there are several guesses all 
    with the maximum expected information, randomly select 
    the guesses that lie in the remaining answer set in the 
    hopes of getting lucky, while maximizing information gain. 
    
    Args
        - guess_information: dict with keys guess, vals expected information
        - possible_answers: list of remaining possible answers from previous outputs
        
    Returns
        - list of lucky information maximizing guesses
    '''
    
    guess, info = np.asarray(list(guess_information.items())).T
    info = info.astype(np.float32)
    
    top_tied_guesses = guess[np.where(info == info.max())[0]]

    lucky_guesses = np.intersect1d(top_tied_guesses,
                                   np.asarray(possible_answers))
    
    return list(lucky_guesses)
