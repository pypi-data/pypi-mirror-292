import pandas as pd
import numpy as np


def remove_blank_spaces(df: pd.DataFrame) -> pd.DataFrame:
    """Remove blank spaces from the beginning and end of the strings in a dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.

    Returns
    -------
    pd.DataFrame
        Dataframe without blank spaces.
    """

    # Eliminar los espacios en blanco antes y después 
    # de los nombres de las columnas
    df.columns = df.columns.str.strip()

    # Eliminar los espacios en blanco antes y después de los valores de las 
    # columnas con valores tipo string
    for columna in df.columns:
        if type(df[columna][0]) == 'str':
            try:
                df[columna] = df[columna].str.strip()
            except Exception as e:
                print(e)
                print(columna)

    return df