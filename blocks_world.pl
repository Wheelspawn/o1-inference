% Define 'above' relation (transitive closure)
above(X, Y) :-
    directly_above(X, Y).
above(X, Y) :-
    directly_above(X, Z),
    above(Z, Y).

% Define 'base_block' to find the base block of a stack
base_block(X, X) :-
    tabled(X).
base_block(X, Base) :-
    directly_above(X, Y),
    base_block(Y, Base).

% Define 'on_different_stack/2'
on_different_stack(X, Y) :-
    base_block(X, BaseX),
    base_block(Y, BaseY),
    BaseX \= BaseY.

% Define 'not_above/2'
not_above(X, Y) :-
    on_different_stack(X, Y).
not_above(X, Y) :-
    base_block(X, Base),
    base_block(Y, Base),
    X \= Y,
    \+ above(X, Y).

