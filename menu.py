
from typing import List, Any


def choose(text: str, options: List, default: str = None) -> (str, Any):
    '''Present menu and verify user input

    text    - The menu text
    options - list of (input[, value], description) tuples
    default - (optional) return this if user just press return

    Where the optional default value has to be of the options list

    Returns a tuple (opt, value)

    Example:

       opt, val = choose('Menu. Pick a choice',
                     (('e', 'Examine surroundings'),
                      ('1', livroom, 'Enter the living room'),
                      ('2', bedroom, 'Enter the bed room'),
                      ('x', 'Exit to outside')),
                     'e')

    This will present a menu where the only allowed inputs from
    the user is e, 1, 2 or x. Options '1' and '2' have an associated
    value that will be returned instead of None as the 2:nd element
    of the return tuple.
    '''

    # Make sure the default is found as an option in the list
    assert not default or default in [opt[0] for opt in options]

    def value_of(tup): return tup[1] if len(tup) > 2 else None

    # Create dict opt -> (opt,value)
    input_dict = dict((tup[0], (tup[0], value_of(tup))) for tup in options)

    while True:
        print(text)
        for tup in options:
            print(f' ({tup[0]}): {tup[-1]}')
        print('\nYour choice:', end=' ')
        inp = input()
        if default and inp == '':
            inp = default
        if inp in input_dict:
            return input_dict[inp]

        print(f'\'{inp.strip()}\' not a valid choice! Try again\n')
