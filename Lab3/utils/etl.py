import pandas as pd
import requests
import arcpy
import arcgis
import os
from os import PathLike
from pandas import DataFrame, Series

class Weather_etl:

    def __init__(self, geodatabase: PathLike, month=1, year=2023):
        self.geodatabase = geodatabase
        self.month = month
        self.year = year
        
        self.fc = f"aggMthWX_{self.month}{self.year}"

        self.url = r"https://mesonet.agron.iastate.edu/api/1/daily.geojson?network=MN_RWIS&month=_M_&year=_Y_".replace(
            "_M_", str(self.month)
        ).replace(
            "_Y_", str(self.year)
        )

    def extract(self) -> DataFrame:
        response = requests.get(self.url)
        json = response.json()["features"]
        df_raw = pd.DataFrame.from_records(json)

        desiredSeries = ["station", "date", "max_tmpf", "min_tmpf", "precip", "name"]

        for s in desiredSeries:
            self._extractToCol(df_raw, s)
            
        df_raw["x"] = df_raw["geometry"].apply(lambda x: dict(x)["coordinates"][0])
        df_raw["y"] = df_raw["geometry"].apply(lambda x: dict(x)["coordinates"][1])

        self.df = df_raw[
            ["station", "date", "max_tmpf", "min_tmpf", "precip", "name", "x", "y"]
        ].copy()

        return self.df

    @staticmethod
    def _extractToCol(df: DataFrame, field: Series) -> None:
        df[field] = df["properties"].apply(lambda x: dict(x)[field])

    def transform(self) -> DataFrame:
        self.df["precip"].fillna(0, inplace=True)

        self.df = self.df.loc[self.df["precip"] >= 0]

        self.df = self.df.dropna(subset=["x", "y", "max_tmpf", "min_tmpf"])

        self.df["station"] = self.df["station"].astype(str)
        self.df["name"] = self.df["name"].astype(str)
        self.df["date"] = self.df["date"].astype("datetime64[ns]")

        self.df = self.df.loc[self.df["x"] > -97.5]
        self.df = self.df.loc[self.df["x"] < -89.0]
        self.df = self.df.loc[self.df["y"] > 43.0]
        self.df = self.df.loc[self.df["y"] < 49.5]

        return self.df

    def aggregate(self) -> DataFrame:
        agg_functions = {
            "station": "first",
            "name": "first",
            "x": "first",
            "y": "first",
            "max_tmpf": "mean",
            "min_tmpf": "mean",
            "precip": "mean",
        }

        self.aggregated_df = self.df.groupby(self.df["station"]).aggregate(
            agg_functions
        )

        return self.aggregated_df

    def load(self) -> None:
        self.sedf = arcgis.GeoAccessor.from_xy(self.aggregated_df, "x", "y")

        self.sedf.spatial.to_featureclass(
            location=os.path.join(self.geodatabase, self.fc)
        )