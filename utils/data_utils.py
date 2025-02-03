import pandas as pd

def cleanup_dataframe(df:pd.DataFrame):
    df.Parents = df.Parents.astype(str)
    df.Parents.loc[df.Parents.str.match('nan')] = None
    df.Parents = df.Parents.str.split('|')

    return df