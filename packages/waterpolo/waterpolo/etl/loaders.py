from pathlib import Path
from typing import Union

import pandas as pd


def load_csv(path: Union[str, Path]) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    if df.columns[0] == "":
        df = df.drop(columns=[""])
    return df
