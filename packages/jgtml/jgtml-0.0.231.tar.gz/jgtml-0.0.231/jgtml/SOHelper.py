import pandas as pd

def get_last_two_bars(df:pd.DataFrame):
  current_bar = df.iloc[-1]
  last_bar_completed = df.iloc[-2:]
  return last_bar_completed,current_bar
  