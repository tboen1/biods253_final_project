## Wordle Solver

This codebase helps you make intelligent guesses when playing wordle, using ideas from information theory! 

### User Guide

The main program in this codebase is `wordle_solver.py`. This program helps you make intelligent guesses,
and comes with the followig arguments. 

- `--board`: this flag allows you to enter the current state of your game as a sequence of guesses and outputs. This sequence can be empty, if you're starting without a guess, or it can be as many pairs of guesses and outputs as  needed. To enter an output, please use the following convention: 

  🟩 = `"G"`, 🟨 = `"Y"`, and ⬜ = `"X"`. 

  For example, if you guessed "crane" and saw ⬜ ⬜ 🟩 ⬜ 🟩, and then "cloud" and saw ⬜ 🟩 ⬜ ⬜ 🟨, you'd enter `--board "crane" "XXGXG" "cloud" "XGXXY"`. 

  This is an optional flag! If you'd like to start a wordle game from scratch we'll happily provide you with a first guess. For mathematical reasons, we really like the word "raise" :)

### Examples

For example, let's say that you guessed "crane" and saw the sequence 🟩 🟨 ⬜ ⬜ ⬜. 

To find the next guess, you could enter in the command `python wordle_solver --board "crane" "GYXXX"`, which would produce the following output. 

```
There are 9 possible answers remaining. 

All Guesses Ranked by Information (* = possible answer)
ivory 3.170  tulip 2.948  sorry 2.948  slurp 2.948  court 2.948 *
viola 3.170  guile 2.948  quirk 2.948  folio 2.948  hovel 2.948  
lorry 3.170  could 2.948  intro 2.948  rumor 2.948  furor 2.948  
glory 3.170  quail 2.948  worry 2.948  ovoid 2.948  fluid 2.948  
... top 20/2315 shown 

Possible Answers Ranked by Information
court 2.948  choir 2.642  curly 2.419  chirp 2.419  curvy 2.059
chord 2.725  curry 2.503  curio 2.419  color 2.419
... top 9/9 shown 

Using the strategy: best_guess, we suggest picking one of: 
ivory  viola  lorry  glory


Using the strategy: best_answer, we suggest picking one of: 
court
```
