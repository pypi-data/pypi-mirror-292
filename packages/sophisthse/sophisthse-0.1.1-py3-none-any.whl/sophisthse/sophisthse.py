import re
from typing import Union
import warnings
import pandas as pd
import requests
from .constants import tables_url, site_encoding, cache_dir


class sophisthse:
    def __init__(
        self,
        to_timestamp: bool = False,
        verbose: bool = False,
    ):
        """Initializes the sophisthse class.

        Args:
            to_timestamp (bool, optional): Whether to convert period index to timestamp.\
                Defaults to True.
            verbose (bool, optional): Whether to display verbose output. Defaults to True.
        """
        self.verbose = verbose
        self.to_timestamp = to_timestamp
        self.tables = self.get_list_of_tables()

    def get_table_url(self, series_name: str) -> str:
        return f"{tables_url}{series_name}.htm"

    def get_list_of_tables(self) -> pd.DataFrame:
        pattern = r"([0-9\/]+\s+[0-9:]+\s+[A,P]M)\s+(?:[0-9]+)\s+[^>]+>([^<]+)<"
        content = requests.get(tables_url).text
        content_list = content.split("<br>")[2:]

        rows = []
        for item in content_list:
            rows.extend(re.findall(pattern, item.strip()))

        df = pd.DataFrame(rows, columns=["date", "name"])

        df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y %I:%M %p")
        df.loc[:, "name"] = df["name"].str.replace(r"\.htm$", "", regex=True)

        return df

    def list_tables(self) -> pd.DataFrame:
        """Returns a pandas DataFrame containing the list of tables.

        Returns:
            pd.DataFrame: A DataFrame with two columns: 'date' and 'name'.
        """
        return self.tables

    @staticmethod
    def __get_period(df: pd.DataFrame) -> str:
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
    def __get_month(t) -> Union[str, None]:
        m = re.sub(r"(?:\d{4}\s)(\d{1,2})", "\\1", t)
        m = m if len(m) <= 2 else None
        return m

    @staticmethod
    def __get_quarter(t) -> Union[str, None]:
        d = {"I": "3", "II": "6", "III": "9", "IV": "12"}
        try:
            q = re.search(r"[IV]+", t).group()  # type: ignore
            return d[q]
        except AttributeError:
            return None

    @staticmethod
    def __get_year(t) -> Union[str, None]:
        try:
            return re.search(r"\d{4}", t).group()  # type: ignore
        except AttributeError:
            return None

    def __get_monthly_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        df.loc[:, ["m"]] = df["T"].apply(self.__get_month)
        df.loc[:, ["y"]] = df["T"].apply(self.__get_year)
        df.loc[:, ["y"]] = df["y"].ffill()
        df.loc[:, "T"] = df.apply(lambda x: x["y"] + " " + x["m"], axis=1)

        df.index = pd.PeriodIndex(df["T"], freq="M")

        if self.verbose:
            print("Monthly dates added to the DataFrame.")

        return df.drop(columns=["T", "m", "y"])

    def __get_quarterly_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        df.loc[:, ["q"]] = df["T"].apply(self.__get_quarter)
        df.loc[:, ["y"]] = df["T"].apply(self.__get_year)
        df.loc[:, ["y"]] = df["y"].ffill()
        df.loc[:, "T"] = df.apply(lambda x: x["y"] + " " + x["q"], axis=1)

        df.index = pd.PeriodIndex(df["T"], freq="Q")

        if self.verbose:
            print("Quarterly dates added to the DataFrame.")

        return df.drop(columns=["T", "q", "y"])

    def __get_yearly_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        df.index = pd.PeriodIndex(df["T"].astype(int), freq="Y")
        df = df.drop(columns=["T"])

        if self.verbose:
            print("Yearly dates added to the DataFrame.")

        return df

    def __compose_path(self, series_name: str) -> str:
        t = self.tables.loc[self.tables["name"] == series_name, "date"].values[0]
        t = pd.to_datetime(t).strftime("%Y%m%d%H%M%S")
        return f"{cache_dir}/{series_name}.{t}.csv"

    def download_table(self, series_name: str, path: str) -> pd.DataFrame:
        """Downloads the data from the website and saves it to a CSV file.

        Args:
            series_name (str): The series name. For example, "BBR_EA_Y_I".
            path (str): The path to save the CSV file.
        Returns:
            pd.DataFrame: The downloaded data as a pandas DataFrame.
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

        if self.verbose:
            print("Data downloaded successfully:", f"{tables_url}{series_name}.htm")

        df = df.dropna(subset=["T"])

        df.to_csv(path, index=False)
        if self.verbose:
            print(f"Table '{series_name}' saved to cache:", path)

        return df

    def get_table(self, series_name: str) -> pd.DataFrame:
        """Returns the data from a table. If the table is not in the cache, it will be downloaded.

        Args:
            series_name (str): The series name. For example, "BBR_EA_Y_I".
        Returns:
            pd.DataFrame: A DataFrame with period index and data in columns.
        """
        path = self.__compose_path(series_name)
        try:
            with open(path, "r") as f:
                df = pd.read_csv(f, parse_dates=False)
                if self.verbose:
                    print(f"Table '{series_name}' loaded from cache.")
        except FileNotFoundError:
            if self.verbose:
                print(f"Table '{series_name}' not found in cache. Downloading from the website.")
            df = self.download_table(series_name, path)

        period = self.__get_period(df)

        if period == "Q":
            df = self.__get_quarterly_dates(df)
        elif period == "M":
            df = self.__get_monthly_dates(df)
        else:
            df = self.__get_yearly_dates(df)

        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        if self.to_timestamp:
            df.index = pd.PeriodIndex(df.index, freq=period).to_timestamp(how="end")

        return df

    def clear_cache(self):
        """
        Clears the cache directory by removing all CSV files.

        Parameters:
            None

        Returns:
            None
        """
        import os

        for file in os.listdir(cache_dir):
            if file.endswith(".csv"):
                os.remove(os.path.join(cache_dir, file))

        if self.verbose:
            print("Cache cleared.")
