# Design Document

### Overview
Wordle is a popular word game in which players attempt to guess a secret 5 letter word in as few tries as possible. For each guess, feedback is given in the form of colored tile indicating when letters match or occupy correct positions. This project helps players make intelligent guesses, using information theory to rank and reccomend different words based on previous guesses and feedback. Information theory is a statistical framework that quantifies the amount of uncertainty or surprise associated with the outcome of an event. In the context of wordle, the feedback of a particular guess is a random variable conditioned on the distribution of possible secret words. A guess that more likely to narrow down the list of possible words, such as by eliminating many possible letters from consideration or confirming the presence of certain letters in specific positions, would have a higher expected information value. Using this mathematical framework, we can quantify how "informative" each possible guess is at any given state in the game by computing its expected information, and so suggest strategically beneficial guesses to players. 

In this project, players can pass in the current state of the board (previous guesses and outputs) into a command line interface, and the program will return a list of guesses ranked by expected information. Using this ranking, the program will then provide two recommendations for the next guess using two different strategies, "best guess" and "best answer". In general, "best guess" is a more cautious strategy that focuses on narrowing down possibilities at the expense of quick wins, while "best answer" trades some informational gain for the chance to get a lucky match. Importantly, the framework does not require that players use this tool from the start, and can provide suggestions at any turn or state of the game, regardless of how many or how few guesses the player has already tried. For example if no previous guesses have been made, the interface would return a ranked list of suggested starting guesses, while after multiple previous guesses and outputs, it may be able to suggest the secret word itself. 


### Background
Wordle is a word game in which players try to guess a secret 5 letter word in as few guesses as possible. After every guess, each letter is marked as either green, yellow or gray: green indicates that the letter is correct and in the correct position, yellow means it is in the answer but not in the right position, while gray indicates it is not in the answer at all. Multiple instances of the same letter in a guess will be colored green or yellow only if the letter also appears multiple times in the answer, with excess repeating letters colored gray. Thus, the key challenge in this game is estimating how useful a guess is to finding the secret word, while incorporating knowledge of previous guesses and outputs. Common strategies involve linguistic heuristics such as vowel testing or letter placement. For example, a starting guess of "raise" is considered quite strong since it tests 3 out of the 5 vowels in the english language, while a guess like "fuzzy" is considered particulary weak since it tests uncommon and duplicated letters. While these heuristics are logical, they are hard to quantify and are not easily generalized, making comparisons between candidate guesses difficult. For example, the comparison between "fuzzy" and "raise" is straightfoward, but evaluating "crate" vs "slate" is not. Our approach resolves these issues by ignoring nebulous heuristics, and instead directly quantifies how much a potential guess helps in narrowing down the number of possibilities for the secret word by calculating its expected information. 

### Goals
This project aims to accomplish the following:
1. **Rank** wordle guesses using statistics calculated from the current state of the game. 
2. **Suggest** wordle guesses using rank statistics and two heuristic strategies, one "greedy" and one "conservative".
3. **Evaluate** the effectiveness of our statistical strategies against appropriate baselines. 

### Non-Goals
This project solely meant to suggest guesses to a wordle player using ideas from information theory. We carefully limit the scope of this project as follows. 

1. We do not seek to create a wordle simulator, we replicate the behavior of the game only insofar as needed to compute relevant statistics
2. This program provides a command line interface, and does not intend to simulate the graphical interface or theme of the original game.
3. We do not seek to design an optimal strategy for solving wordle games. While we rank and suggest guesses to users in a principled fashion, the final choice lies with the player, and we make no guarantees on whether our methods are optimal.
4. We will evaluate the effectiveness of both strategies and appropriate baselines (my personal performance and random selection), but as before, we will not compare against any other "state-of-the-art" solvers if there are any.


### Future Goals
We regard this project as fairly self contained. However, some interesting strategies would be to incorporate relative word frequencies into our guess valuation strategies. More specifically, we assume a uniform distribution over all possible secret words at any given turn, and calculate the expected information of each guess by calculating the likelihood of each possible color output under this uniform distribution. While this a reasonable assumption, it is quite conservative, as not all 5 letter words are equally likely. For example, in the current implementation, if the final word was narrowed down to be one of "gulch", "mulch" or "lunch", all three would have probability 1/3. However, given their frequency in usage, it would seem reasonable to first guess "lunch", then "mulch", and finally "gulch". 

### Detailed Design

#### User Requirements
The user-facing program in this project is presented as a command line interface, and does not include any type of graphical user interace. As such, users will expected to be familiar with the basics of Unix systems. However, we make sure to include user manuals that can be quickly accessed with help flags, for example, by running `python wordle_solver.py -h`. 

#### Structure
This project is structured into several components. 

Required files.
1. `wordle_words.txt` a list of official wordle words. All guesses and suggested answers will be drawn from this file. Noteable, this project cannot suggest a guess not contained in this file, so it is important to ensure that the game is using the official list and not an expanded library.
2. `env.yml` a conda environment file for installing the required dependencies for this project. 

Generated files
1. `starting_guesses.csv` is a precomputed list of ranked starting guesses that is automatically generated the first time `wordle_solver.py` is run. This precomputation enables lower latency for future usage.
2. `/results` is a folder containing simulation results generated by `strategy_simulator.py`. 

User facing programs
1. `wordle_solver.py` allows users to enter the state of the wordle board, and receive guess suggesstions. This is the main user facing program and is anticipated for repeated usage (e.g. entering multiple outputs and recieving guess suggestions over the course of a game). 
2. `strategy_simulator.py` allows users to benchmark the performance of the `best_guess` and `best_answer` strategies. This is a user facing program, but is not anticipated to be run very often.

Internal Libraries
1. `tests.py` contains unit tests checking the behavior of various components.
2. `utils.py` contains helpful code blocks for implementing various functionalities.
   
Misc 
1. `Analysis.ipynb` is a jupyter notebook for analyzing the performance of the `best_guess` and `best_answer` strategies using the outputs of `strategy_simulator.py`.

#### Throughput/Latency
Of the programs listed above, only `wordle_solver.py` is required to have low latency. Users can query `wordle_solver.py` at any stage of the game, and can thus reasonably be expected to call this program multiple times in a row. As such, `wordle_solver.py` uses vectorized numpy code to quickly rank and suggest guesses. In addition, a list of ranked first guesses is automatically generated the first time `wordle_solver.py` is run. In contrast, `strategy_simulator.py` is required to have high throughput, since it evaluates strategies over all possible wordle words (2315 in the official list) under multiple repetitions. As such, `strategy_simulator.py` uses extensive precomputation to speed up simulations, and replace repeated computations with a quick lookup. 

#### Testing/Validation
Testing is accomplished using `tests.py`, and checks that the behavior of the expected information calculations and guess suggestions reflects the behavior of the official wordle rules, particularly regarding the official word list and output behavior of repeated letters. 

#### APIs
This project does not require any APIs. 

#### Logging/monitoring/observability
This project is self contained, and does not report any usage information. 

#### Privacy/Security
This project does not use any sensitive information. 

### Third-Party Dependencies
External dependencies are encapsulated in `env.yml`, which is an enviroment file for generating a reproducible conda environment with all the required dependencies. This project is designed to be fairly lightweight, and so only requires common python scientific computing libraries, e.g. numpy, scipy, pandas etc. 

### Alternative approaches
Information theory is very naturally suited to the gameplay of wordle, and we selected this approach for its elegence and generalizability. However, there are alternatives and extensions. As previously discussed, one method would be to introduce linguistic heuristics that better reflect the behavior of human players. While this approach is more interpretable, for example by reporting vowel counts instead of bits of information, it is not a scalable or effective strategy due to inherent difficulties in quantifying the value between syntactically similar words. A more advanced strategy is to incorportate word frequencies from the english language, and thus help choose "likely" guesses. This is a more promising strategy that could be readily ammended to our information theory framework, however, we weren't sure whether true games could be expected to have a preference for common vs rare words, or whether they only cared about whether a word was contained in the official wordle words list. Thus, for this iteration, we elected to choose a more generalizable, if potentially less efficient, strategy. 









