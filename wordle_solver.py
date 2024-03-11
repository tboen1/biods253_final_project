import numpy as np
import pandas as pd
from tqdm import tqdm

import cmd

import argparse

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
                display(guess_df, ["best_info", "best_answer"])

            return guess_df

def display(guess_df, strategies_list, n=20):
    '''
    Nicely formats and prints outputs
    
    Args
        - guess_df: pandas dataframe with columns guess (str), 
                    information (float), and possible answer (bool)
        - strategies_list: list of best_answer, best_info, random_answer
    
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
    
    
