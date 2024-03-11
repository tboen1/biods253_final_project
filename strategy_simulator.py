import numpy as np
import pandas as pd

from tqdm import tqdm
import pickle as pk
import os

import argparse

from utils import (load_words,  
                   next_guess_options,
                   guess2color,
                   filter_answers,
                   get_expected_information,
                   build_guess_df)

from wordle_solver import (execute_wordle_solver,
                           check_data)

def play_game(secret_word: str, first_guess: str, strategy: str, valid_words: list, 
                                                  precomputed_outputs: dict = None):
    '''
    Plays one game of wordle
    
    Args
        - secret_word: secret word
        - first_guess: first guess
        - strategy: one of best_answer, best_guess, or random_answer
        - valid_words: set of wordle words
        - precomputed_outputs: precomputed answer-guess output pairs
    '''
    
    if precomputed_outputs is None:
        output = guess2color(secret_word, first_guess)
    else:
        output = precomputed_outputs[(secret_word, first_guess)]
        
    board = [first_guess, output]

    while "GGGGG" not in board:    

        reshaped_board = [(board[i], board[i + 1]) for i in range(0, len(board), 2)]
        possible_answers = filter_answers(reshaped_board, valid_words, 
                                          precomputed_outputs = precomputed_outputs)

        if strategy in ["best_answer", "best_guess"]:

            guess_information = get_expected_information(guesses = valid_words, 
                                                         answers = possible_answers,
                                                         show_progress = False,
                                                         precomputed_outputs = precomputed_outputs)

            guess_df = build_guess_df(guess_information, possible_answers)
            guess_options = next_guess_options(guess_df, strategy)

        else: #random_answers
            guess_options = possible_answers

        next_guess = np.random.choice(guess_options)

        if precomputed_outputs is None:
            output = guess2color(secret_word, next_guess)
        else:
            output = precomputed_outputs[(secret_word, next_guess)]

        board.extend([next_guess, output])
        
    return board

def evaluate_strategy(strategy: str, valid_words: list, starting_guesses: pd.DataFrame,
                                                        precomputed_outputs: dict = None):
    '''
    Simulates Wordle Strategy Performance
    
    Args
        - strategy: one of best_answer, best_guess, or random_answer
        - valid_words: set of wordle words
        - starting_guesses: dataframe with precomputed guesses and 
                            information values for first guess
        - precomputed_outputs: precomputed answer-guess output pairs
        
    Returns
        - full_results: dict with keys secret word, 
                        values board of guesses and results
    '''

    if strategy in ["best_answer", "best_guess"]:
        #pick best first guess out of precomputed guesses
        starting_guess = starting_guesses[starting_guesses["information"] == 
                                       starting_guesses["information"].max()]["guess"].values[0]
    elif strategy == "random_answer":
        starting_guess = None
    
    else:
        raise ValueError("strategy must be one of 'best_answer', 'best_guess', or 'random_answer'")

    full_results = {}
    
    for idx, secret_word in tqdm(enumerate(valid_words), total = len(valid_words)):
        
        if starting_guess is not None:
            first_guess = starting_guess
            
        else:
            first_guess = np.random.choice(list(valid_words))
            
        full_results[secret_word] = play_game(secret_word, first_guess, strategy, valid_words, 
                                              precomputed_outputs = precomputed_outputs)
        
    return full_results

def run_simulations(strategy_list: list, valid_words: list, starting_guesses: pd.DataFrame, 
                    results_dir: str, num_reps: int):
    '''
    Runs strategy simulations
    
    Args
        - strategy_list: list containing best_answer, best_guess, or random_answer
        - valid_words: list of wordle words
        - starting_guesses: dataframe with precomputed guesses and 
                            information values for first guess
        - results_dir: where to save results
        - num_reps: number of repetitions
    '''
    
    print("Starting evaluation \n")
    
    print("Precomputing color scores ... ")
    
    precomputed_outputs = {}
    for answer in tqdm(valid_words, total = len(valid_words)):
        for guess in valid_words:
            color = guess2color(answer, guess)
            precomputed_outputs[(answer, guess)] = color
    
    for rep in range(num_reps):
    
        for strategy in strategy_list:
            print("starting {} strategy simulation".format(strategy))

            full_results = evaluate_strategy(strategy, valid_words, starting_guesses, precomputed_outputs)

            file_name = "{}/{}_strategy_full_results_rep={}.pk".format(results_dir, strategy, rep)
            pk.dump(full_results, open(file_name, "wb"))

            print("Finished! saved results to {}".format(file_name))
        
    print("All done!")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument("-results_dir", help = "path to results folder", type = str)
    parser.add_argument("--num_reps", help = "number of repetitions", type = int, default = 10)
    parser.add_argument("--strategy_list", help = "strategies to simulate", nargs = "*", type = str, default = ["best_guess",
                                                                                                           "best_answer", 
                                                                                                           "random_answer"])
    parser.add_argument("--data_dir", help = "directory with wordle_words.txt", default = "data", type = str)
    
    args = parser.parse_args()
    
    valid_words, starting_guesses = check_data(args)
    
    if not os.path.isdir(args.results_dir):
        print("Warning! {} directory not found, creating directory".format(args.results_dir))
        os.makedirs(args.results_dir)

    run_simulations(args.strategy_list, valid_words, starting_guesses, args.results_dir, args.num_reps)
        
        
    
    
    
