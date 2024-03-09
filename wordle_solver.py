import numpy as np
import pandas as pd
from tqdm import tqdm

import cmd

import argparse

from utils import (load_words, 
                   guess2color, 
                   get_color_distribution, 
                   get_expected_information,
                   postprocessing_heuristic)

def execute_wordle_solver(board, valid_words, starting_guesses, verbose = True):
    
    #TODO supress prints for fast simulation testing
    
    if len(board) == 0:
        
        print("WELCOME TO WORDLE!")
        print("There are {} possible answers remaining".format(len(valid_words)))
        print("Try these guesses to start: \n")

        print(starting_guesses.head())
        
    else:
        possible_answers = valid_words
        for (guess, output) in board:
            
            if output == "GGGGG":
                print("Congratulations! The correct answer was {}".format(guess))
                return None
            
            else:      
                color_distribution = get_color_distribution(guess, possible_answers)
                possible_answers = color_distribution[output]
            
        guess_information = get_expected_information(guesses = valid_words, 
                                                     answers = possible_answers,
                                                     show_progress = True)
        
        lucky_guesses = postprocessing_heuristic(guess_information, possible_answers)
        
        display(possible_answers, guess_information, lucky_guesses)
   
        return guess_information, possible_answers, lucky_guesses

def display(possible_answers, guess_information, lucky_guesses):
    '''
    Nicely formats and prints outputs
    
    Args
        - possible_answers: remaining words that satisfy previous outputs
        - guess_information: dict with keys guess, vals information
        - lucky_guesses: list of potentially lucky glesses
    
    Returns
        - None. Simply prints nice looking messages
    '''
    
    cli = cmd.Cmd()
    
    next_guess = pd.DataFrame({"guess": list(guess_information.keys()),
                                  "information": list(guess_information.values())})
    
    print("There are {} possible answers remaining: \n".format(len(possible_answers)))
        
    cli.columnize(list(possible_answers)[:30], displaywidth=80)
    if len(possible_answers) > 30: print("...")

    print("\nGuesses Ranked by Expected Information: \n")
    print(next_guess.head())

    if len(lucky_guesses) == 0:
        print("\nWe suggest picking: {} \n".format(list(guess_information.keys())[0]))
        
    elif len(lucky_guesses) == 1:
        print("\nWe suggest picking: {} \n".format(lucky_guesses[0]))
        
    else:
        print("\nWe suggest picking one of these guesses, each are equally good, but you could get lucky! \n")
        cli.columnize(list(lucky_guesses)[:30], displaywidth=80)
        if len(lucky_guesses) > 30: print("...")
            
    print("\n")        
    
    
def config(args):
    '''
    Cleans up arguments and ensures correct behavior
    
    Args
        - board: Previous wordle guesses and outputs
        - words_file: List of wordle words
        - starting_guesses: precomputed starting guesses
    
    Returns
        - reshaped_board: N x 2 list of guesses and outputs
        - words_file: wordle words as set
        - starting_guesses: saves starting guesses to csv
    '''
    
    ############ Board ############
    board = args.board
    
    if len(board)%2 != 0:
        raise ValueError("unequal number of guesses and outputs!")
    
    reshaped_board = [(board[i], board[i + 1]) for i in range(0, len(board), 2)]
    
    final_board = []
    for (guess, output) in reshaped_board:
        
        if (len(guess) != 5 or len(output) != 5):
            raise ValueError("inputs and outputs must be 5 letters!")
            
        if (not guess.isalpha() or not output.isalpha()):
            raise ValueError("inputs and outputs can only contain letters!")
            
        if not set(list(output)).issubset(set(list("XYG"))):
            raise ValueError("outputs must be X: grey,Y: yellow, or G: green")
            
        final_board.append((guess.lower(), output.upper()))
    
    ############ Words File ############
    try:
        valid_words = load_words(args.words_file)
    except:
        print("words file: {} not found!".format(args.words_file))
        raise 
    
    ############ Starting Guesses ############
    try:
        starting_guesses = pd.read_csv(args.starting_guesses, index_col = 0)
    except:
        print("Precomputed starting guesses not found, computing now ... ")
        
        guess_information = get_expected_information(guesses = valid_words, 
                                                     answers = valid_words,
                                                     show_progress = True)
        suggested_guesses = pd.DataFrame({"guess": list(guess_information.keys()),
                                  "information": list(guess_information.values())})
        suggested_guesses.to_csv(args.starting_guesses)
        
        print("DONE! Starting guesses saved to: {}".format(ags.starting_guesses))
        
    return final_board, valid_words, starting_guesses
    

if __name__ == "__main__":
    
    help_message = (
    '''
    
    A wordle board is a sequence of guesses and outputs. 
    
    Example:
    
    first guess: "adieu" yields "gray, yellow, gray, gray, yellow"
    second guess: "bound" yields "gray, green, green, green, green"

    board = "adieu" "XYXXY" "bound" "XGGGG"
        
    Note: Gray -> X, Yellow -> Y, Green -> G 
    
    '''
    )
    
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--board", help = help_message, type = str, nargs = "*", default = [])
    parser.add_argument("--words_file", help = "list of words", default = "wordle_words.txt", type = str)
    parser.add_argument("--starting_guesses", help = "starting guesses", default = "starting_guesses.csv", type = str)
    
    args = parser.parse_args()
    
    final_board, valid_words, starting_guesses = config(args)
    
    execute_wordle_solver(final_board, valid_words, starting_guesses)
    
    
