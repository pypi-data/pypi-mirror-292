import re
from typing import Union
import warnings
import pandas as pd
import requests
from .constants import tables_url, site_encoding


class sophisthse:
    def __init__(
        self,
        to_timestamp: bool = True,
        verbose: bool = True,
    ):
        """Initializes the sophisthse class.

        Args:
            to_timestamp (bool, optional): Whether to convert period index to timestamp.\
                Defaults to True.
            verbose (bool, optional): Whether to display verbose output. Defaults to True.
        """
        self.verbose = verbose
        self.tables_url = tables_url
        self.to_timestamp = to_timestamp

    def get_table_url(self, series_name: str) -> str:
        return f"{tables_url}{series_name}.htm"

    def list_tables(self) -> pd.DataFrame:
        """Returns a pandas DataFrame containing the list of tables.

        Returns:
            pd.DataFrame: A DataFrame with two columns: 'date' and 'name'.
        """
        pattern = r"([0-9\/]+\s+[0-9:]+\s+[A,P]M)\s+(?:[0-9]+)\s+[^>]+>([^<]+)<"
        content = requests.get(self.tables_url).text
        content_list = content.split("<br>")[2:]

        rows = []
        for item in content_list:
            rows.extend(re.findall(pattern, item.strip()))

        df = pd.DataFrame(rows, columns=["date", "name"])

        df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y %I:%M %p")
        df.loc[:, "name"] = df["name"].str.replace(r"\.htm$", "", regex=True)
        return df

    @staticmethod
    def get_period(df: pd.DataFrame) -> str:
        date_str = df.iloc[0, 0]

        if re.match(r"\d{4}\s[IV]+", str(date_str)):
            return "Q"
        if re.match(r"\d{4}\s\d{1,2}", str(date_str)):
            return "M"
        if re.match(r"\d{4}", str(date_str)):
            return "Y"
        else:
            raise ValueError("The date format is not recognized.")

    @staticmethod
    def get_month(t) -> Union[str, None]:
        m = re.sub(r"(?:\d{4}\s)(\d{1,2})", "\\1", t)
        m = m if len(m) <= 2 else None
        return m

    @staticmethod
    def get_quarter(t) -> Union[str, None]:
        d = {"I": "3", "II": "6", "III": "9", "IV": "12"}
        try:
            q = re.search(r"[IV]+", t).group()  # type: ignore
            return d[q]
        except AttributeError:
            return None

    @staticmethod
    def get_year(t) -> Union[str, None]:
        try:
            return re.search(r"\d{4}", t).group()  # type: ignore
        except AttributeError:
            return None

    def get_monthly_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        df.loc[:, ["m"]] = df["T"].apply(self.get_month)
        df.loc[:, ["y"]] = df["T"].apply(self.get_year)
        df.loc[:, ["y"]] = df["y"].ffill()
        df.loc[:, "T"] = df.apply(lambda x: x["y"] + " " + x["m"], axis=1)

        df.index = pd.PeriodIndex(df["T"], freq="M")

        if self.verbose:
            print("Monthly dates added to the DataFrame.")

        return df.drop(columns=["T", "m", "y"])

    def get_quarterly_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        df.loc[:, ["q"]] = df["T"].apply(self.get_quarter)
        df.loc[:, ["y"]] = df["T"].apply(self.get_year)
        df.loc[:, ["y"]] = df["y"].ffill()
        df.loc[:, "T"] = df.apply(lambda x: x["y"] + " " + x["q"], axis=1)

        df.index = pd.PeriodIndex(df["T"], freq="Q")

        if self.verbose:
            print("Quarterly dates added to the DataFrame.")

        return df.drop(columns=["T", "q", "y"])

    def get_yearly_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        df.index = pd.PeriodIndex(df["T"].astype(int), freq="Y")
        df = df.drop(columns=["T"])

        if self.verbose:
            print("Yearly dates added to the DataFrame.")

        return df

    def get_table(self, series_name: str) -> pd.DataFrame:
        """Returns the data from a table.

        Args:
            series_name (str): The series name. For example, "BBR_EA_Y_I".
        Returns:
            pd.DataFrame: A DataFrame with period index and data in columns.
        """
        warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

        url = self.get_table_url(series_name)
        df = pd.read_html(
            url,
            decimal=",",
            thousands=".",
            na_values="&nbsp",
            encoding=site_encoding,
            header=0,
        )[0]
        df = df.dropna(subset=["T"])

        period = self.get_period(df)

        if period == "Q":
            df = self.get_quarterly_dates(df)
        elif period == "M":
            df = self.get_monthly_dates(df)
        else:
            df = self.get_yearly_dates(df)

        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        if self.to_timestamp:
            df.index = pd.PeriodIndex(df.index, freq=period).to_timestamp(how="end")

        if self.verbose:
            print("Data loaded successfully from:", f"{tables_url}{series_name}.htm")

        return df
