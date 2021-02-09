'''
A simple utility that helps you train foreign vocabularies.

It has the following features:
  - Gives you incitament to train by offering a leveling system!
  - Levels are per training file and persistent!
  - You get the chance to add and change translations if your answer was
    falsely incorrect. This is remembered!
  - Automatically detects vocabulary files as files ending with '_voc.txt'!
'''

# System modules
import os
import pickle  # The module we use to save and load state

# Local modules
import session
import savestate

GREETING = '''
*** VOC TRAIN ***
    Version 2.0
    (C) 2020 Eleonora Svanberg

Hello and welcome!
'''

STATEFILE = 'trainee.pkl'


def main() -> None:
    '''Voctrain main entry function'''

    print(GREETING)

    if os.path.exists(STATEFILE):
        with open(STATEFILE, 'rb') as fd:
            tstate = pickle.load(fd)
    else:
        # Create an empty initial TraineeState
        tstate = savestate.TraineeState()

    try:
        session.run_session(tstate)
    except KeyboardInterrupt:
        print('\nCtrl-C pressed.\n'
              'Exiting vocabulary training. Saving level state.')
    finally:
        with open(STATEFILE, 'wb') as fd:
            pickle.dump(tstate, fd)


main()
