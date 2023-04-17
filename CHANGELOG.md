# CHANGELOG

Additional information about work done for various commits.

## Skeleton Work - 2023.04.02

1. Created class to handle server queries.
2. Added dummy server to test against

## Algorithm Improvements - 2023.04.06

1. Repackaged all strategy related functions into class `TTTStrategy` in `TTTStrategy.py`
2. Move maker functions and the parallel worker is now in `TTTMoveMaker.py`
3. Added `TTTAgent.py`
    a. `TTTAgent` can handle all communication with the server by itself
    b. `TTTAgent` calls move maker to make moves and then post it back to the server 
    c. `TTTAgent` now reads a game setup file (e.g. `game-TEMPLATE.json`) to start. Please see comments in `game-TEMPLATE.json`.
    d. `TTTAgent` also reads the header file (e.g. `key-TEMPLATE.json`) to store info on the HTTP header info, the default file header file name is `key.json`.
4. Parallelized pattern check codes and packaged them into a method for TTTStrategy now.

## Interface Additions - 2023.04.16

1. Added `tester.py` to make sure key functions work appropriately.
2. Modified `project3.py` to work with the latest algorithms
    a. It can function as an alternate interface for the project
3. Added `settings.json` to specify which team IDs should use which algorithms when playing
4. Moved changelog to separate file
