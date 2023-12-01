import os
from typing import Dict

import pandas as pd
from dotenv import load_dotenv

# from IPython import get_ipython
from pandas import DataFrame, Series

load_dotenv()


def get_env(env_variable: str) -> str:
    env_value = os.getenv(env_variable)
    if env_value is None:
        print(f"{env_variable} is None")
        return ""
    else:
        return env_value


MART_PROD = f"mssql+pyodbc://jie_zhang:{get_env('DWH_PASSWORD_JIE')}@nbea-dev-use2-sql.public.209f1e31ec07.database.windows.net:3342/MART_PROD?Encrypt=yes&TrustServerCertificate=yes&driver=ODBC+Driver+18+for+SQL+Server"
DEV_FINTECH = f"mssql+pyodbc://jie_zhang:{get_env('DWH_PASSWORD_JIE')}@nbea-dev-use2-sql.public.209f1e31ec07.database.windows.net:3342/DEV_FINTECH?driver=ODBC+Driver+18+for+SQL+Server"
FLEX_LOCAL = f"mysql+mysqldb://admin:{get_env('MYSQL_PASSWORD_LOCAL')}@host.docker.internal:3306/flex"

# ipython = get_ipython()
# ipython.run_line_magic("load_ext", "sql")

hint = """%load_ext sql
supported DB:
    %sql $MART_PROD
    %sql $DEV_FINTECH
    %sql $FLEX_LOCAL
"""
print(hint)


def save_dfs_to_excel(dfs: Dict[str, DataFrame], filename: str) -> None:
    """
    Save multiple DataFrames to an Excel file, each DataFrame in a separate sheet,
    using xlsxwriter as the engine.

    Parameters:
    dfs (dict): A dictionary of DataFrames, where keys are sheet names.
    filename (str): The filename of the Excel file.
    """
    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
