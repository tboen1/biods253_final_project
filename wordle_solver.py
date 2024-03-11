import numpy as np
import pandas as pd
from tqdm import tqdm

import cmd

import argparse
import os

from utils import (load_words, 
                   guess2color, 
                   get_color_distribution, 
                   get_expected_information,
                   build_guess_df, 
                   next_guess_options,
                   filter_answers)

def execute_wordle_solver(board: list, valid_words: list, starting_guesses: pd.DataFrame, 
                                                                verbose: bool = True, 
                                                                show_progress: bool = True,
                                                                precomputed_outputs: dict = None):
    
    '''
    Suggests guesses for wordle games depending on board. 
    
    Args
        - board: list of tuples guess and inputs
        - valid_words: list of wordle words
        - starting_guesses: dataframe with columns guess and information for first guess
        - verbose: print outputs or not
        - show_progress: show tqdm progress bar
        - precomputed_outputs: cached input output pairs
        
    Returns
        - guess_df: dataframe with columns guess and information for next guess
    '''
    
    
    if len(board) == 0:
        
        print("WELCOME TO WORDLE!")
        print("There are {} possible answers remaining".format(len(valid_words)))
        print("Try these guesses to start: \n")

        print(starting_guesses.head())
        
    else:
        possible_answers = valid_words
        
        if "GGGGG" in np.asarray(board).ravel() and verbose:
            print("Congratulations! The correct answer was {}".format(board[-1][0]))
            return None
        
        else:
            try:
                possible_answers = filter_answers(board, valid_words, 
                                                  precomputed_outputs = precomputed_outputs)
            except:
                print("We're sorry. There don't seem to be any answers that fit those outputs.")
                return None
            
            guess_information = get_expected_information(guesses = valid_words, 
                                                         answers = possible_answers,
                                                         show_progress = show_progress,
                                                         precomputed_outputs = precomputed_outputs)

            guess_df = build_guess_df(guess_information, possible_answers)

            if verbose:
                display(guess_df, ["best_guess", "best_answer"])

            return guess_df

def display(guess_df, strategies_list, n=20):
    '''
    Nicely formats and prints outputs
    
    Args
        - guess_df: pandas dataframe with columns guess (str), 
                    information (float), and possible answer (bool)
        - strategies_list: list of best_answer, best_guess, random_answer
    
    Returns
        - None. Simply prints nice looking messages
    '''
    
    all_guesses_output = []
    all_answers_output = []

    for index, row in guess_df.iterrows():
        row_str = "{} {:.3f}".format(row.guess, row.information)

        if row.possible_answer:
            all_answers_output.append(row_str)
            all_guesses_output.append(row_str + " *")
        else:
            all_guesses_output.append(row_str)

    cli = cmd.Cmd()
    
    print("There are {} possible answers remaining. \n".format(guess_df['possible_answer'].sum()))
    
    print("All Guesses Ranked by Information (* = possible answer)")
    cli.columnize(all_guesses_output[:n], displaywidth=80)
    print("... top {}/{} shown \n".format(len(all_guesses_output[:n]), len(all_guesses_output)))

    print("Possible Answers Ranked by Information")
    cli.columnize(all_answers_output[:n], displaywidth=80)
    print("... top {}/{} shown \n".format(len(all_answers_output[:n]), len(all_answers_output)))

    
    for strategy in strategies_list:
        
        next_guess = next_guess_options(guess_df, strategy)
        
        print("Using the strategy: {}, we suggest picking one of: ".format(strategy))
        cli.columnize(next_guess, displaywidth=80)
        print("\n")       
    
def check_board(board: list):
    '''
    Cleans up board and ensures correct behavior
    
    Args
        - board: Previous wordle guesses and outputs
    
    Returns
        - reshaped_board: N x 2 list of guesses and outputs
    '''
        
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
        
    return final_board

def check_data(data_dir: str):
    '''
    Checks for words file and precomputed guesses within data_dir. 
    
    If precomputed guesses aren't found, precomputes them. 
    
    Args
        - data_dir. Expects words file inside to be called "wordle_words.txt"
        
    Returns
        - potentially saves starting_guesses.csv into data_dir
    '''
    
    #checking data directory
    if os.path.isdir(data_dir):
        pass
    else:
        raise ValueError("data directory: {} does not exist!".format(data_dir))
    
    #checking words file
    words_file = "{}/wordle_words.txt".format(data_dir)
    
    if os.path.isfile(words_file):
        valid_words = load_words(words_file)
    else:
        raise ValueError("wordle_words.txt not found in {}!".format(data_dir))
        
    #checking precomputed starting guesses
    starting_guesses_file = "{}/starting_guesses.csv".format(data_dir)
    
    if os.path.isfile(starting_guesses_file):
        starting_guesses = pd.read_csv(starting_guesses_file, index_col = 0)
    else:
        print("Precomputed starting guesses not found, computing now ... ")
        
        guess_information = get_expected_information(guesses = valid_words, 
                                                     answers = valid_words,
                                                     show_progress = True)
        starting_guesses = pd.DataFrame({"guess": list(guess_information.keys()),
                                  "information": list(guess_information.values())})
        starting_guesses.to_csv(starting_guesses_file)
        
        print("DONE! Starting guesses saved to: {}".format(starting_guesses_file))
        
    return valid_words, starting_guesses
    

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
    parser.add_argument("--data_dir", help = "directory with wordle_words.txt", default = "data", type = str)
    
    args = parser.parse_args()
    
    final_board = check_board(args.board)
    valid_words, starting_guesses = check_data(args.data_dir)
    
    execute_wordle_solver(final_board, valid_words, starting_guesses)
    
    
