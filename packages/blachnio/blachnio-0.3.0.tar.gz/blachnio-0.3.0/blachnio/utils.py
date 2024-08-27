from blachnio.decors import printout


@printout('List ot object attributes:')
def show_attributes(item):
    """Displays object attributes."""

    def _print_attributes(list_of_attributes, max_col_width, max_digits_number):
        cols = 3
        counter = 1
        for i, attr in enumerate(list_of_attributes):
            print(f'[{i:{max_digits_number}}] {attr}', ' ' * (max_col_width - len(attr)), end=' ')
            if counter == cols:
                counter = 0
                print('\n', end='')
            counter += 1
        if counter > 1:
            print()

    dunders = [i for i in dir(item) if i.startswith('_')]
    nondunders = [i for i in dir(item) if not i.startswith('_')]
    col_width = max(map(len, dunders + nondunders))
    digits_number = max(len(str(len(dunders))), len(str(len(nondunders))))
    print('Dunders:')
    if dunders:
        _print_attributes(dunders, col_width, digits_number)
    print('\nNonDunders:')
    if nondunders:
        _print_attributes(nondunders, col_width, digits_number)
