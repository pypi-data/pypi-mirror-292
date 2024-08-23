# Wordler!
Wordler! is an app for solving Wordle puzzles. In its current form, Wordler! is a 
command line interface (CLI) app, but work on a web app is underway, too. 

Using Wordler! is pretty straightforward. First, you provide your initial guess to the
app, and then it will ask if this initial guess solved the possible. If the puzzle has 
not been solved, the app will then ask for Wordle's feedback on the guess. Wordler! 
will display the letter in the guess, and you'll select which letters Wordle has 
highlighted green and which letters Wordle has highlighted yellow. 

Wordler! will then take this information and provide you with a new guess - along with 
a probability that this guess is the answer to the puzzle - to enter into Wordle. It 
will then go through the same steps of asking if the puzzle has been solved, and if 
not asking for the green and yellow tiles. Wordler! solves the puzzle almost all of 
the time, and on average, takes about 3.65 guess (including your initial guess) to find 
the correct word.

Check out the example of Wordler! solving the puzzle for the word "meter" below:

![](assets/Wordler!.gif)

# Installation
The Wordler! CLI app has been published to PyPI and can be installed with PIP. 
```
pip install wordler-cli
```

You can also build the CLI app directly from source by running the following in an 
environment of your choosing:
```
pip install git+https://github.com/k-bartolomeo/wordler.git
```

# Methodology
Wordler! starts off with sets of all possible letters for each position in a word. As
it receives feedback from the Wordle game itself, it will update these sets of letters. 
For example, if the correct word is `meter` and the guess word is `tried`, Wordle will 
mark the `e` in `tried` green and the `t` and the `r` yellow. After receiving this 
information from the user, Wordler! will then update the set of possible letters for 
each position as follows:
- Remove `t` from the set of possible letters for the first position.
- Remove `r` from the set of possible letters for the second position.
- Reduce the set for the fourth position to just the letter `e`, since that is the 
correct letter.
- Remove the letters `i` and `d` from all position sets since they are not in the 
goal word.
- Update the set of letters that must be included in the next guess to include `t`, 
`r`, and `e` if they are not present in the set already.

From there, Wordler! will update the list of remaining possible words based on the 
letters available for each position. Then, it will compute a probability for each 
remaining word using a combination of letter probabilities given word positions, 
transition probabilities from one letter to the next, and usage probabilities. The 
need for the first two probabilities is pretty self-evident; the inclusion of the 
usage probabilities, on the other hand, is based on the assumption that the NY Times 
editor choosing the Wordle words will be more likely to choose words that are used 
more often, as opposed to words with which the general public may be less familiar.

As far as the calculation of these various probabilities goes, the letter probabilities 
given the word positions are computed using counts of each letter in each position in 
the words in the Wordle corpus. Similar counts from the words in the Wordle corpus are 
used for the transition probabilities. These transition counts also consider word 
position in order to account for the fact that the probability of a transition, for 
example, from `letter 1` to `letter 2` might be higher if `letter 1` is the first letter
in the word instead of the third letter in the word. Usage probabilities are taken from 
[this subset](https://www.kaggle.com/datasets/rtatman/english-word-frequency) of usage 
counts derived from the Google Web Trillion Word Corpus.

# Web App
A web application that offers the same functionality as the CLI, albeit in a more 
aesthetically pleasing manner, is currently under development. This application is being 
built using mostly Python and the Dash framework, with a small bit of JavaScript sprinkled
in. The basic layout of the application is pictured below, and the code that has been 
written for the app thus far can be found on the `app-dev` branch of this repository.

![](<assets/Wordler! App.png>)