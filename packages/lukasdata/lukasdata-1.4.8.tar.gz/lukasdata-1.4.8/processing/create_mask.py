import pandas as pd


def create_in_mask(iterable1, iterable2, case_sensitive=True):

    if not case_sensitive:
        if isinstance(iterable1, pd.Series):
            iterable1 = iterable1.str.lower()
        else:
            iterable1 = [str(i).lower() for i in iterable1]
        
        if isinstance(iterable2, pd.Series):
            iterable2 = iterable2.str.lower()
        else:
            iterable2 = [str(i).lower() for i in iterable2]
    else:
        if not isinstance(iterable1, pd.Series):
            iterable1 = [str(i) for i in iterable1]
        
        if not isinstance(iterable2, pd.Series):
            iterable2 = [str(i) for i in iterable2]
    mask = [element in iterable2 for element in iterable1]
    return mask
