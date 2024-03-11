import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt

def load_words(fp: str):
    '''
    Loads list of all english words that contain only letters
    
    Params:
        fp: file path to wordle word list
    '''
    
    with open(fp) as word_file:
        valid_words = set(word_file.read().split())

    return list(valid_words)

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

def get_color_distribution(guess: str, possible_answers: list,
                           show_progress: bool = False, 
                           precomputed_outputs: dict = None):
    '''
    Given a guess and a set of possible answers, 
    computes the distribution of possible color outputs
    as a dictionary. 
    
    Args:
        - guess: Word to guess
        - possible_answers: set of potential answers
        - show_progress: display tqdm progress bar
        - precomputed_outputs: precomputed answer-guess output pairs
        
    Returns:
        - dist: Dictionary with keys outputs and values
                list of words that could've generated that output
    '''
    
    dist = {}
    
    for answer in tqdm(possible_answers, total = len(possible_answers),
                       disable = not show_progress):
        
        if precomputed_outputs is None:
            output = guess2color(answer = answer, guess = guess)
        else:
            output = precomputed_outputs[(answer, guess)]
        
        if output in dist.keys():
            dist[output].append(answer)
        
        else:
            dist[output] = [answer]
            
    return dist

def get_expected_information(guesses: list, answers: list, 
                             return_sorted: bool = True,
                             show_progress: bool = False,
                             precomputed_outputs: dict = None):
    '''
    Given a set of guesses and a set of possible answers, 
    computes the expected information of each guess. 
    
    That is, for a given guess g, it's expected information E_g[I]
    is given by: 
    
    E_g[I] = - Sum_x p(x) log_2(p(x))
    
    Where x indicates a color output, and p(x) indicates 
    the probability of that color output occuring given the 
    set of possible answers. 
    
    Args:
        - guesses: set of guess words
        - answers: set of possible answer words
        - return_sorted: sort by decreasing information 
        - show_progress: display tqdm progress bar
        - precomputed_outputs: precomputed answer-guess output pairs
        
    Returns: 
        - guess_information: dictionary with keys guesses andd 
                             values expected information for that guess
    '''
    
    guess_information = {}
    
    for g in tqdm(guesses, total = len(guesses), disable = not show_progress):
        color_dist = get_color_distribution(guess = g, 
                                            possible_answers = answers, 
                                            show_progress = False,
                                            precomputed_outputs = precomputed_outputs)

        num_matches = np.asarray([len(x) for x in list(color_dist.values())])
        
        p_vals = num_matches/np.sum(num_matches)

        expected_information = -np.sum(p_vals * np.log2(p_vals))
        
        guess_information[g] = expected_information
        
    if return_sorted:
        guess_information = dict(sorted(guess_information.items(), 
                                   key=lambda item: item[1], 
                                   reverse = True))
        
    return guess_information

def build_guess_df(guess_information: dict, possible_answers: list):
    '''
    Structures guesses
    
    Args
        - possible_answers: list of possible answers
        - guess_information: dict with keys guess and values information
        
    Returns
        - guess_df: pandas dataframe with columns guess (str), 
                    information (float), and possible answer (bool)
    '''
    
    guess_df = pd.DataFrame({"guess": list(guess_information.keys()),
                         "information": list(guess_information.values())})
    
    guess_df['possible_answer'] = guess_df["guess"].apply(lambda x: x in possible_answers)
    
    return guess_df


def next_guess_options(guess_df: pd.DataFrame, strategy: str):
    '''
    Offers choices for the next guess based on strategy
    
    Args:
        - guess_df: pandas dataframe with columns guess, 
                    info, and possible answer
        - strategy: one of best_answer, best_guess, or random_answer
                 
                 - best_answer:
                         picks possible answers with highest information. 
                 
                 - best_guess: 
                         picke guesses with highest information. 
                         If a guess or guesses has both the highest information 
                         and is a possible answer, this guess is selected. 
                         
                - random_answer:
                         randomly selects guesses that are possible answers
    
    Returns:
        - list of guesses
    '''
    
    if strategy == "best_answer":
        
        choice_df = guess_df[guess_df["possible_answer"]]
        max_info = choice_df['information'].max()
        
        #guesses with maximum info that are possible answers
        best_answer = choice_df[choice_df["information"] == max_info]["guess"].values
        
        return list(best_answer)
        
    elif strategy == "best_guess":
        
        choice_df = guess_df
        max_info = choice_df['information'].max()
        
        #guesses with maximum info, including ties
        best_guess_guess = choice_df[choice_df["information"] == max_info]["guess"].values
        
        #guesses with maximum info that are also possible answers, including ties
        best_guess_answer = choice_df[(choice_df["information"] == max_info) & 
                                    (choice_df["possible_answer"])]['guess'].values
        
        if len(best_guess_answer) > 0:
            return list(best_guess_answer)
        
        else:
            return list(best_guess_guess)
        
    elif strategy == "random_answer":
        
        #any possible answer
        choice_df = guess_df[guess_df['possible_answer']]
        
        return list(choice_df['guess'].values)
    
    else:
        raise ValueError("strategy must be one of 'best_answer', 'best_guess', or 'random_answer'")
        
def filter_answers(board: list, possible_answers: list, precomputed_outputs: dict = None):
    '''
    Filters possible anwers based on previous guesses and outputs
    
    Args
        - board: list of tuples, guess and output. 
        - possible_answers: list of candidate words
        - precomputed_outputs: precomputed answer-guess output pairs

    Returns
        - possible_answers: list of possible words
    '''
    for (guess, output) in board:      
        color_distribution = get_color_distribution(guess, possible_answers, 
                                                    precomputed_outputs = precomputed_outputs)
        possible_answers = color_distribution[output]
        
    return possible_answers
