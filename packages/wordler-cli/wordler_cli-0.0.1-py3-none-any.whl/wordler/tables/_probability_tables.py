import string
import warnings

from itertools import pairwise

import pandas as pd
import numpy as np
from numpy import typing as npt


warnings.filterwarnings('ignore')


class ProbabilityTables:
    """Container class for probability tables
    
    Represents all words in Wordle corpus as '#<word>', where  the 
    '#' symbol is a start token. Builds two probability matrices and 
    stores them as attributes. First matrix is a three-dimensional 
    transition matrix with shape (5, 27, 27). First axis represents 
    each letter-to-letter transition in a word, i.e. start symbol to
    letter 1, letter 1 to letter 2, letter 2 to letter 3, letter 3 to
    letter 4, and letter 4 to letter 5. Second axis represents starting
    letter in transition and includes dimension for start symbol. Third
    axis represents ending letter in transition and also includes 
    dimension for start symbol.

    Second matrix holds letter probabilities given word positions and 
    has shape (6, 27). First axis is letter position and includes 
    dimension for start symbol. Second axis is letter in given position
    and also includes dimension for start symbol.
    
    Class holds list of all words in corpus, as well as mapping of 
    letters to indices and indices back to letters.

    Attributes
    ----------
    letter_map : dict
        Mapping of characters to index values.
    letter_lookup : dict
        Mapping of index values back to characters.
    word_data : pd.DataFrame
        pandas DataFrame holding words within Wordle corpus and 
        corresponding usage counts.
    words : list[str]
        List of words in Wordle corpus with '#' start symbol added
        as prefix.
    transition_matrices : npt.NDArray
        Three-dimensional NumPy array of letter transition matrices
        with shape (5, 27, 27). First axis represents transition start 
        position, second axis represents starting letter in transition, 
        and third axis represens ending letter in transition.
    position_matrix : npt.NDArray
        Two-dimensional NumPy array of letter probabilities given word
        positions with shape (6, 27). First axis represents word 
        position and includes the start symbol. Second axis represents
        letters, also including the start symbol.

    Parameters
    ----------
    word_data
        Path to CSV file storing words in Wordle corpus and 
        corresponding usage counts.
    """
    def __init__(self, word_data: str) -> None:
        self.letter_map = {k:v for v,k in enumerate('#' + string.ascii_lowercase)}
        self.letter_lookup = {k:v for k,v in enumerate('#' + string.ascii_lowercase)}
        self.word_data = pd.read_csv(word_data)
        self.word_data['p'] = self.word_data['count'] / self.word_data['count'].sum()
        self.words = [f'#{w}' for w in self.word_data['word'].tolist()]
        self.transition_matrices = self._init_transition_matrices()
        self.position_matrix = self._init_position_probabilities()

    def _init_transition_matrices(self) -> npt.NDArray:
        """Builds three-dimensional matrix of transition probabilities"""
        transition_matrices = [np.zeros((27, 27)) for _ in range(5)]
        for w in self.words:
            letters = [self.letter_map[letter] for letter in w]
            for i, pair in enumerate(pairwise(letters)):
                np.add.at(transition_matrices[i], pair, 1)

        # Normalize counts to get probabilities and convert NaN
        # values to 0.
        for i, matrix in enumerate(transition_matrices):
            transition_matrices[i] = np.nan_to_num(matrix / matrix.sum(1)[:, None], 0)

        transition_matrices = np.stack(transition_matrices)
        return transition_matrices
    
    def _init_position_probabilities(self) -> npt.NDArray:
        """Builds two-dimensional matrix of position probabilities"""
        position_matrix = np.zeros((6, 27))
        for w in self.words:
            letters = [self.letter_map[letter] for letter in w]
            np.add.at(position_matrix, (np.arange(6), letters), 1)

        # Normalize counts to get probabilities.
        position_matrix /= position_matrix.sum(1)[:, None]
        return position_matrix
    