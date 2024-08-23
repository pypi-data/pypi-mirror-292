import operator
from functools import reduce
from itertools import pairwise

from ..tables import ProbabilityTables


class Solver:
    """Calculates word probabilities and makes guesses

    Handles calculation of positional probabilities, transition 
    probabilities, and usage probabilities. Calculates word probability
    through multiplication of positional, transition, and usage 
    probabilities. Also handles narrowing down of search space given
    Wordle feedback, i.e. yellow and green letter tiles and their 
    positions. Makes guesses based on maximum calculated probability
    across all remaining words in search space.

    Attributes
    ----------
    letter_map : dict
        Mapping of characters to index values.
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
    word_data : pd.DataFrame
        pandas DataFrame holding words within Wordle corpus and 
        corresponding usage counts.
    words : list[str]
        List of words in Wordle corpus with '#' start symbol added
        as prefix.
    
    Parameters
    ----------
    tables : ProbabilityTables
        Initialized instance of ProbabilityTables class storing word
        information and probability matrices.
    """
    def __init__(self, tables: ProbabilityTables) -> None:
        self.letter_map = tables.letter_map
        self.position_matrix = tables.position_matrix
        self.transition_matrices = tables.transition_matrices
        self.word_data = tables.word_data
        self.words = tables.words

    def get_positional_probability(
        self, word: str, candidates: list[set]
    ) -> list[float]:
        """Calculates position probability of each letter
        
        Probability of letter given position taken from 
        `ProbabilityTables` instance used to initialize class. 
        Probability of letter in first position skipped because 
        letter will always be start symbol '#' and will therefore 
        have probability 1

        Parameters
        ----------
        word
            Word for which positional probabilities of letters are
            calculated.
        candidates
            List of sets of possible letters remaining for each
            position.

        Returns
        -------
        list[float]
            List of positional probabilities of letters.
        """
        word_prob = []
        for i, letter in enumerate(word):
            if i == 0:
                continue
            candidate_letters = [self.letter_map[x] for x in candidates[i]]
            position_prob = self.position_matrix[i].copy()

            # Need to set positional probabilities for letters either
            # not included in the word or not included at the given
            # position to be 0. This will give the desired outcome of 
            # a 0 word probability for this word.
            for letter_idx in set(range(27)) - set(candidate_letters):
                position_prob[letter_idx] = 0.

            # Re-normalize probabilities after having set probabilities
            # of impermissible letters in certain positions to 0.
            position_prob /= position_prob.sum()
            letter_prob = position_prob[self.letter_map[letter]]
            word_prob.append(letter_prob)

        return word_prob


    def get_usage_prob(self, word: str, remaining_words: list[str]) -> float:
        """Gets usage probability of given word
        
        Filters usage data to include only those words that are within
        search space given Wordle's feedback thus far. Re-normalizes
        probabilities within this subset and extracts usage probability
        for given word.

        Parameters
        ----------
        word
            Word for which usage probability is found.
        remaining_words
            List of remaining words in search space given feedback
            from Wordle.

        Returns
        -------
        float
            Usage probability of given word.
        """
        subset = (
            self.word_data[
                self.word_data.word.isin([w[1:] for w in remaining_words])
            ].copy()
        )
        subset['p'] = subset.p / subset.p.sum()
        usage_prob = subset[subset.word == word[1:]].p.iloc[0]
        return usage_prob
    
    def get_transition_probabilities(self, word: str) -> list[float]:
        """Gets transition probabilities for letters in given word"""
        probs = [
            self.transition_matrices[i, p[0], p[1]]
            for i, p in enumerate(
                pairwise([self.letter_map[letter] for letter in word])
            )
        ]
        return probs

    def get_word_prob(
        self, word: str, candidates: list[set], remaining_words: list
    ) -> float:
        """Calculates word probability

        For given word, gets transition and positional probabilities
        of letters. Also gets usage probability of word itself. 
        Multiplies all of these probabilities together to get single
        worlde probability.

        Parameters
        ----------
        word
            Word for which word probability is calculated.
        candidates
            List of sets of possible letters remaining for each
            position.
        remaining_words
            List of remaining words in search space given feedback
            from Wordle.

        Returns
        -------
        float
            Word probability.
        """
        probs = self.get_transition_probabilities(word=word)
        probs.extend(self.get_positional_probability(word=word, candidates=candidates))
        probs.append(self.get_usage_prob(word=word, remaining_words=remaining_words))
        return reduce(operator.mul, probs)


    def check_word(
        self, word: str, candidates: list[set], must_include: set[str]
    ) -> bool:
        """Determines if given word should be included in search space
        
        Checks if the following conditions are met:
            1. All letters that the goal word must include per 
               Wordle's feedback are included in the given word.
            2. For each letter and its corresponding position in the 
               word, the letter is still in the list of remaining 
               possible letters for that position.

        Parameters
        ----------
        word
            Word to check for inclusion in search space.
        candidates
            List of sets of possible letters remaining for each
            position.
        must_include
            Set of letters that must be included in goal word per
            Wordle's feedback.

        Returns
        -------
        bool
            Boolean denoting whether or not the given word could be 
            the goal word given the game state.
        """
        if not all(letter in word for letter in must_include):
            return False
        if word[0] not in candidates[0]:
            return False
        if word[1] not in candidates[1]:
            return False
        if word[2] not in candidates[2]:
            return False
        if word[3] not in candidates[3]:
            return False
        if word[4] not in candidates[4]:
            return False
        if word[5] not in candidates[5]:
            return False
        return True


    def make_guess(
        self,
        results: list[int],
        previous_guess: str,
        must_include: set[str],
        candidates: list[set],
        remaining_words: list
    ) -> tuple[str, float, set, list[set], list]:
        """Makes next word guess given game state

        Wordle feedback for previous guess stored as list of integers 
        where 0 denotes a gray tile (letter not included in goal word),
        1 denotes a yellow tile (letter included in word but not in 
        given position), and 2 denotes a green tile (letter included in
        word at given position). Set of remaining letters for each 
        position updated based on this feedback, and then list of 
        remaining words in search space updated based on that. Word
        probability for each remaining word is calculated, and next 
        guess becomes word with maximum probability.

        Parameters
        ----------
        results
            List of integers denoting feedback on previous guess from 
            Wordle.
        previous_guess
            Previous guess given to Wordle.
        must_include
            Set of letters that must be included in goal word per
            Wordle's feedback.
        candidates
            List of sets of possible letters remaining for each
            position.
        remaining_words
            List of remaining words in search space given feedback
            from Wordle.
        
        Returns
        -------
        tuple[str, float, set, list[set], list]
            Five-item tuple. First item is next guess to be given to
            Wordle. Second item is computed probability of next guess.
            Third item is updated set of letters that the goal word 
            must include. Fourth item is updated list of sets of 
            remaining letters for each position. Fifth item is updated
            list of remaining words in search space.
        """
        for i, (result, letter) in enumerate(zip(results, previous_guess)):
            # If Wordle says letter not in goal word, remove letter from 
            # set of possible letters for all positions if it hasn't 
            # already been removed (e.g., letter is duplicate of letter
            # in same word and that has already been removed).
            if result == 0:
                if letter not in must_include:
                    for pos in candidates:
                        if letter in pos:
                            pos.remove(letter)
                else:
                    if letter in candidates[i]:
                        candidates[i].remove(letter)
            # If Wordle says letter in goal word but not in position 
            # given in previous guess, remove letter from set of 
            # possible letters for that position and add it to set of
            # letters taht goal word must include.
            elif result == 1:
                if letter in candidates[i]:
                    candidates[i].remove(letter)
                must_include.add(letter)
            # If Wordle says letter in goal word and in correct position,
            # make set of possible letters for that position only this
            # letter and add this letter to set of letters goal word 
            # must include.
            else:
                candidates[i] = set(letter)
                must_include.add(letter)

        # Update list of words remaining in search space given Wordle
        # feedback and updated candidate sets.
        remaining_words = [
            word for word in remaining_words 
            if self.check_word(
                word=word, candidates=candidates, must_include=must_include
            )
        ]

        # Calculate word probabilities of remaining words, sort them,
        # and select word with highest probability as next guess.
        remaining_word_probs = [
            self.get_word_prob(
                word=word,
                candidates=candidates, 
                remaining_words=remaining_words
            ) 
            for word in remaining_words
        ]
        sorted_probs = sorted(
            zip(remaining_words, remaining_word_probs), key=lambda x: x[1]
        )
        total_probs = sum([x[1] for x in sorted_probs])
        guess = sorted_probs[-1][0]
        guess_prob = sorted_probs[-1][1] / total_probs

        return guess, guess_prob, must_include, candidates, remaining_words
