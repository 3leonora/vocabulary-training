'''
    Class definitions for the user's training state that gets saved.

    This is what gets saved through pickling of a TraineeState object:

    * The current voc file the user has selected (if any)
    - Per voc file:
       * The level of the user
       * Whether the user has qualified for examination
       * Additional translations for english words
       * Translations of an english word to not consider from the voc file
'''


class VocState:
    '''Holds user related info given a specific vocabulary file

    1. What level the user has
    2. If the user is qualified to level up (take the exam)
    3. Any extra allowed translations
    '''

    def __init__(self):
        '''Setup defaults'''
        self._level = 0           # Trainee level for this vocabulary set
        self._is_qualified = False   # May take exam to level
        self._extra_trans = {}    # Extra translations provided by user

    def num_of_modifs(self):
        '''Return the number of user added translation modifications'''
        return sum(len(addrm[0] | addrm[1]) for addrm
                   in self._extra_trans.values())

    def change_translation(self,
                           engword: str,
                           add: set = set(),
                           remove: set = set()):
        '''Add and remove valid translations for a word

        add - set of words to add
        remove - set of words to remove
        '''
        addset, rmset = self._extra_trans.setdefault(engword, (set(), set()))
        addset |= add
        addset -= remove
        rmset |= remove
        rmset -= add

    def get_modified_translations(self,
                                  engword: str,
                                  translations: list) -> set:
        '''Apply corrections to a word's default translations

        Modify a vocabulary's default list of allowed translations. The
        function can add new allowed translations, but also remove one
        or more translations from the given ones.

        engword       - The english word
        translations  - List of translations we start with

        Returns a set of allowed translations
        '''

        addset, rmset = self._extra_trans.get(engword, (set(), set()))
        result = set(translations)
        result |= addset  # Add elements in addset to result
        result -= rmset   # Remove elements in rmset from result
        return result

    def reset_modifications(self, engword: str):
        '''Reset any modification to the translation of the given word'''
        if engword in self._extra_trans:
            del self._extra_trans[engword]

    @property
    def level(self): return self._level
    @level.setter
    def level(self, lev): self._level = lev

    @property
    def qualified(self): return self._is_qualified
    @qualified.setter
    def qualified(self, q): self._is_qualified = q


class TraineeState:
    '''Holds all state that should be persistent between runs'''

    def __init__(self):
        self._current_voc = ''          # File name of current vocabulary set
        self._voc_states: VocState = {}  # The state objects per vocabulary

    # The propery 'voc_file' reflects the user's current selected
    # vocabulary. It can be both read and set.
    @property
    def voc_file(self): return self._current_voc
    @voc_file.setter
    def voc_file(self, filepath): self._current_voc = filepath

    @property
    def current_voc_state(self):
        '''Return the current vocabulary user state.

        This method creates, stores and returns a fresh state if it doesn't
        previously exist.
        '''
        return self._voc_states.setdefault(self._current_voc, VocState())

    def print_all_stats(self, maxlevel: int):
        '''Print the current trainee status for all vocabularies

        maxlevel    - Needed for nicer printout.
        '''
        print('\n------ Trainee states -----\n')
        fmt = '%-2s%-30s%10s%15s%11s'
        print(fmt %
              ('', 'Vocabulary', 'Level', '#Translations', 'Qualified'))
        print()

        for k, v in self._voc_states.items():

            # Decide what to write under "Qualified"
            if v.level == maxlevel:
                qual = 'Master'
            elif v.qualified:
                qual = 'Yes'
            else:
                qual = 'No'

            # Decide the 'Current voc file' column tag
            curstr = ' '
            if k == self._current_voc:  # Mark current with '*'
                curstr = '*'

            print(fmt % (curstr, k, v.level, v.num_of_modifs(), qual))

        print('\n    * = current selected vocabulary')
