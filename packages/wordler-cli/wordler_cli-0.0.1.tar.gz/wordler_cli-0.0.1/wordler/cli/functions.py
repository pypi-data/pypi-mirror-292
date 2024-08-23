from collections import defaultdict

import questionary
from questionary import prompt


def process_word(word: str) -> list[str]:
    """Creates representations of letter based on letter counts
    
    In CLI options provided by Questionary, need to differentiate
    between same letter in different positions. If this is not done,
    any single selection of a duplicate letter will result in the 
    selection of all duplicates of that letter, which is not the 
    desired outcome. Differentiation is accomplished by modifying 
    the string representation of the letter based on the number of 
    occurences of the letter in the given word.

    Parameters
    ----------
    word
        Word to process.

    Returns
    -------
    list[str]
        List of letter representations based on letter counts in word
        and taking form '<letter><letter-count>'.

    Example
    -------
    >>> word = 'aback'
    >>> letters = process_word(word=word)
    >>> letters
    ['a1', 'b1', 'a2', 'c1', 'k1']
    """
    letter_counts = defaultdict(int)
    letter_reprs = []
    for letter in word:
        letter_counts[letter] += 1
        letter_reprs.append(f'{letter}{letter_counts[letter]}')
        
    return letter_reprs


def get_tile_results(
    choices: list[dict],
    letter_reprs: list[str],
    results: list[int],
    kind: str = 'green'
) -> list[int]:
    """Prompts user to provide Wordle's feedback

    Asks user to select either green or yellow tiles within word
    based on feedback provided by Wordle. Updates results list
    based on information received.

    Parameters
    ----------
    choices
        List of dictionaries having two keys, `name` and `value`.
        Value for `name` key is normal string representation of letter,
        and value for `value` key is letter representation created by
        `process_word` function.
    letter_reprs
        List of letter representations created by `process_word` 
        function.
    results
        List of integers denoting Wordle's feedback on previous guess.
    kind
        Whether or not information retrieved from user relates to 
        green tiles or yellow tiles.

    Returns
    -------
    list[int]
        Updated list of results based on information received from
        user.
    """
    tiles = questionary.checkbox(
        f'Select the {kind} tiles:',
        choices=choices,
    ).ask()

    # Green tiles are represented with integer value 2, yellow tiles 
    # are represented with integer value 1, and gray tiles are 
    # represented with integer value 0. `tiles` retrieved from user
    # are in same form as `letter_reprs` values, so `letter_reps` 
    # list used to index into `results` list.
    value = 2 if kind == 'green' else 1
    for tile in tiles:
        results[letter_reprs.index(tile)] = value

    return results


def get_results(guess: str) -> list[int]:
    """Gets Wordle feedback from user
    
    Passes previous guess through `process_word` function to create 
    choices used in prompts to user. Retrieves positions of yellow and 
    green tiles in previous guess and uses this information to update
    results list.

    Parameters
    ----------
    guess
        Previous word guess.

    Returns
    -------
    list[int]
        List of integers denoting feedback from Wordle. Value of 2 
        represents green tile, value of 1 represents yellow tile, and
        value of 0 represents gray tile.
    """
    letter_reprs = process_word(guess[1:])
    choices = [{'name': letter[0], 'value': letter} for letter in letter_reprs]
    results = [0 for _ in range(5)]
    results = get_tile_results(choices, letter_reprs, results, kind='green')
    results = get_tile_results(choices, letter_reprs, results, kind='yellow')
    results = [2] + results
    return results


def print_next_guess(guess: str, guess_prob: float) -> None:
    """Prints next guess and its probability"""
    prompt([{
        "type": "print",
        "name": "next_guess",
        "message": (
            f"\n\U0001F50D Next guess: {guess.lstrip('#')} "
            f"(p={guess_prob*100:.2f}%) \U0001F50D\n"
        ),
    }])


def print_solved() -> None:
    """Prints congratulatory message after puzzle solved"""
    prompt([{
        "type": "print",
        "name": "next_guess",
        "message": (
            "\n\U0001F973 \U0001F388 \U0001F389 \U0001F913 "
            "Congratulations, WordNerd! \U0001F913 \U0001F389 "
            "\U0001F388 \U0001F973"
        )
    }])
    print()


def get_solved() -> bool:
    """Checks whether or not puzzle was solved with previous guess"""
    response = prompt([{
        "type": "confirm",
        "name": "solved",
        "message": "Is the puzzle solved?",
        "default": False,
    }])
    solved = response['solved']
    return solved


def get_initial_guess(remaining_words: list[str]) -> str:
    """Gets initial guess from user
    
    Checks if word in Wordle corpus. If not, user will not be able 
    to move to next guess.

    Parameters
    ----------
    remaining_words
        List of words in Wordle corpus.

    Returns
    -------
    str
        User's initial guess for puzzle.
    """
    response = prompt([{
        "type": "text",
        "name": "initial_guess",
        "message": "Please enter your initial guess:",
        "validate": lambda x: f'#{x}' in remaining_words,
    }])
    guess = f"#{response['initial_guess']}"
    return guess
