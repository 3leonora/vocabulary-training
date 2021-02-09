'''
User interaction and state update logic in voctrain application
'''

import os
from typing import List, Tuple, Dict
import random

# Local modules
from savestate import TraineeState, VocState
import menu

# How many words in a exam/training session
# Has to be 10 to cover all words in a vocabulary,
# but can be lowered when testing.
_NUMWORDS = 10

_MAXLEVEL = 10

# The type of the list we construct from the vocabulary file
VocTable = List[Tuple[str, List[str]]]


def _read_voc(tstate: TraineeState) -> VocTable:
    '''Retrieve a vocabulary table

    Read a vocabulary from the file stated in the trainee state object.

    tstate   -  A trainee state object

    returns a list of words and their translations.

    '''
    voctable = []

    with open(tstate.voc_file, 'tr') as fd:
        for line in fd:
            _, translations, engword = line.split('\t')
            # Allow for comma separated multiple translations of eng word
            voctable.append((engword.strip(),
                             [t.strip() for t in translations.split(',')]))

    return voctable


def _print_banner(text: str, width: int):
    '''Print some text surrounded by lines

    text    - The message
    width   - How many characters in line
    '''

    print('-' * width)
    print(text.center(width))
    print('-' * width)


def _clear_screen():
    '''Clear the terminal'''
    print(chr(27) + '[2J')


def _switch_voc(tstate: TraineeState) -> str:
    '''Let user choose from all found .voc files

    tstate    - trainer state object

    When a valid file name has been chosen the tstate is updated
    with that info.

    Return true if the vocabulary changed.
    '''

    old_voc_file = tstate.voc_file

    i = 1
    menuopts = []
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if f.endswith('_voc.txt'):
            menuopts.append((str(i), f, f'The vocfile {f}'))
            i += 1

    # If no _voc.txt file was found
    if not menuopts:
        print("\033[93mWARNING:"
              " No _voc.txt file was found. Exit program and "
              "change file name to end with '_voc.txt'.\033[0m")

    # Add the option to not choose file
    menuopts.append(('q', 'go back without choosing file'))

    choice, vocfile = menu.choose('[Select Vocabulary Menu]'
                                  ' Please choose a vocabulary to train.',
                                  menuopts)

    if choice != 'q':
        tstate.voc_file = vocfile

    return tstate.voc_file != old_voc_file


def _setup_test(vstate: VocState, voctable: VocTable) -> Dict[str, List[str]]:
    '''Return dict of default translations for given level

    vstate      - trainee state for given (=current) vocabulary
    voctable    - full table (= all levels) of vocabulary

    returns a dict where key is the english word and value is a list of
    translations as found in the vocabulary file.
    '''
    startix = _NUMWORDS * vstate.level
    return dict((voctable[startix:startix + _NUMWORDS]))


def _take_exam(vstate: VocState, voctable: VocTable):
    '''Take the exam to try level up

    vstate      - trainee state for given (=current) vocabulary
    voctable    - full table (= all levels) of vocabulary
    '''

    vocdict = _setup_test(vstate, voctable)
    # Randomize the order we test
    testwords = list(vocdict.keys())
    random.shuffle(testwords)

    _clear_screen()
    _print_banner(f'LEVEL {vstate.level + 1} EXAM!', 40)

    for num, engword in enumerate(testwords):
        translations = vstate.get_modified_translations(
            engword, vocdict[engword])
        print(f'{num + 1}: How do you say \'{engword}\'? ', end='')
        answer = input().lower()
        if answer in translations:
            print('  Correct!')
            del vocdict[engword]  # Remove it from the rest of the session.
        else:
            break  # No use to continue the exam...

    if not vocdict:
        print('\nYou finished the exam with no errors! Good work!')
        vstate.level += 1
        vstate.qualified = False  # Not qualified any longer!
        print(f'Level up! New level for this vocabulary is {vstate.level}.')
        print('Press return', end='')
        input()
    else:
        print('\nYou failed the exam. Better luck next time!')


def _modify_translation(engword: str,
                        answer: str,
                        translations: set,
                        vstate: VocState):
    '''Let user choose how a rejected translation should be handled.

    engword      - The english word to potentially modify translation for
    answer       - The user's translation that might actually be correct
    translations - The current set of valid translations
    vstate       - The VocState object containing any modifications to
                   the default translation of the engword

    '''

    # Menu options always available
    menuopts = [('0', '[Default] Do nothing. My translation was wrong.'),
                ('a', f"Add '{answer}' to translations"),
                ('r', f"Reset to original translation of '{engword}'")]

    # Add menu options for replacing a word. We associate the replacement
    # word with the option as the 2nd arg in the option tuple. See menu.choose.
    for n, word in enumerate(translations, start=1):
        menuopts.append((str(n), word, f"Replace '{word}' with '{answer}'"))

    opt, replaceword = menu.choose(
        '[Add/Modify Translation] What would you like to do?', menuopts, '0')

    if opt == '0':
        print('Ok. Continuing.\n')
    elif opt == 'a':
        print(f"Ok. Adding '{answer}' as a valid translation\n")
        vstate.change_translation(engword, add={answer})
    elif opt == 'r':
        print(f"Ok. Clearing all changes to translations of '{engword}'\n")
        vstate.reset_modifications(engword)
    else:  # Request replacing a word ( = value part of menu option)
        print(f"Ok. Replacing '{replaceword}' with '{answer}'\n")
        vstate.change_translation(engword, add={answer}, remove={replaceword})


def _train(vstate: VocState, voctable: VocTable):
    '''Run a training session

    vstate      - trainee state for given (=current) vocabulary
    voctable    - full table (= all levels) of vocabulary
    '''

    vocdict = _setup_test(vstate, voctable)

    _print_banner(f'Level {vstate.level} training session', 40)

    def get_translations(engword):
        return vstate.get_modified_translations(engword, vocdict[engword])

    keepon = True

    while keepon:
        # Randomize the order of remaining words
        testwords = list(vocdict.keys())
        numwords = len(testwords)
        random.shuffle(testwords)

        print(f'Starting test round of {len(testwords)} words.\n')

        for num, engword in enumerate(testwords):
            translations = get_translations(engword)
            print(f'{num + 1}: How do you say \'{engword}\'? ', end='')
            answer = input().lower()
            if answer not in translations:
                # Ok - wrong answer. Give the user a chance to add the
                # word to the vocabulary
                correct = " or ".join(f"'{w}'" for w in translations)
                print(f'Not correct. It should be {correct}.')
                _modify_translation(engword, answer, translations, vstate)
            else:
                print('  Correct!')
                del vocdict[engword]  # Remove it from the rest of the session.

        if not vocdict:  # If all words been translated correctly at least once
            print('\nYou seem to know all the words!')
            if not vstate.qualified:
                if vstate.level < _MAXLEVEL:
                    print('You are now qualfied to take the exam!')
                vstate.qualified = True
            keepon = False

        else:  # There are still words we've not translated correctly
            print('\nDone. You got '
                  f'{numwords - len(vocdict)}/{numwords} correct!\n')
            print('Difficult words:')
            print('----------------')
            for engword in vocdict.keys():
                translations = get_translations(engword)
                print(f'  {engword} -> {", ".join(translations)}')

            # At this point the user can exit the training if they like

            menutext = "[Training Menu] Would you like to continue training?"
            menuopts = [('c', 'Continue with difficult words?'),
                        ('x', 'Exit to main menu')]
            if menu.choose(menutext, menuopts)[0] == 'x':
                keepon = False
            else:
                _clear_screen()


def run_session(tstate: TraineeState):
    '''Main menu logic.

    tstate - The state that got read from file

    This functions run until the user selects the 'q' option (quit).
    From here one can select different vocabularies, train and do an
    exam when one has qualified.
    '''

    # If vocabulary configured in the state we load it.
    if tstate.voc_file:
        voctable = _read_voc(tstate)
    else:
        voctable = None

    remain_running = True

    while remain_running:

        print('-' * 60)

        # These menu options are always there
        menuopts = [('c', 'Change or set vocabulary file'),
                    ('l', 'Show levels for vocabularies')]

        # Some menu options are added conditionally below

        if not voctable:
            print("\033[93mNo vocabulary file selected. "
                  "Please select! (option 'c')\033[0m")
        else:
            print(f'  Current vocabulary: {tstate.voc_file}')
            level = tstate.current_voc_state.level
            print(f'  Level: {level}')

            if level == _MAXLEVEL:
                qualstr = '(you are max level - no more exams to do)'
            else:
                menuopts.append(('t', 'Start training sub session'))
                if tstate.current_voc_state.qualified:
                    qualstr = 'Yes!'
                    menuopts.append(('e', 'Take exam'))
                else:
                    qualstr = 'No'
            print(f'  Qualified for exam: {qualstr}')

        # Nice to have the quit option furthest down
        menuopts.append(('q', 'Quit and save'))

        choice, _ = menu.choose('\n[Main Menu]: Pick an operation!', menuopts)
        print()

        if choice == 'c':
            if(_switch_voc(tstate)):
                voctable = _read_voc(tstate)
        elif choice == 'q':
            print('Ok. See you soon!')
            remain_running = False
        elif choice == 't':
            _train(tstate.current_voc_state, voctable)
        elif choice == 'e':
            _take_exam(tstate.current_voc_state, voctable)
        elif choice == 'l':
            tstate.print_all_stats(_MAXLEVEL)
            print()
