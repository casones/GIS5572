import arcpy
import os
import pandas as pd
from typing import Union
from pandas import DataFrame
from os import PathLike

class Pipeline:

    def __init__(
        self,
        point_feature_class: PathLike,
        output_directory: PathLike,
        output_geodatabase: PathLike,
        value_of_interest: str,
    ) -> None:
        self.point_feature_class = point_feature_class
        self.output_directory = output_directory
        self.output_geodatabase = output_geodatabase
        self.value_of_interest = value_of_interest

        self.feature_name = os.path.split(self.point_feature_class)[1]
        self.stats_table = f"{self.feature_name}_stats"
        self.geostats_layer = f"{self.feature_name}_bestInterpolator"
        self.interpolation_methods = "ORDINARY_KRIGING;UNIVERSAL_KRIGING;IDW"

        arcpy.env.workspace = self.output_geodatabase

    def run_exploratory_interpolation(self) -> None:
        arcpy.ga.ExploratoryInterpolation(
            self.point_feature_class,
            self.value_of_interest,
            self.stats_table,
            self.geostats_layer,
            self.interpolation_methods,
            "SINGLE",
            "ACCURACY",
            "ACCURACY PERCENT #",
            "ACCURACY 1",
            None,
        )

        print(arcpy.GetMessages())
    
    def display(self, display_method: str) -> Union[str, DataFrame]:
        arcpy.conversion.ExportTable(
            self.stats_table,
            os.path.join(self.output_directory, f"{self.stats_table}.csv"),
        )

        df = pd.read_csv(os.path.join(self.output_directory, f"{self.stats_table}.csv"))

        if display_method == "PRINT":
            return print(df)

        elif display_method == "DATAFRAME":
            return df
        
        else:
            if type(display_method) == str:
                raise ValueError(
                    "Param 'display_method' must be in ['PRINT', 'DATAFRAME']"
                )
            else:
                raise TypeError(
                    "Param 'display_method' must be of type string and value of ['PRINT', 'DATAFRAME']"
                )
            
    def create_point_accuracy_layer(self) -> None:
        self.point_accuracy_path = os.path.join(
            self.output_geodatabase, f"{self.feature_name}_point_diff"
        )

        arcpy.ga.GALayerToPoints(
            self.geostats_layer,
            self.point_feature_class,
            None,
            self.point_accuracy_path,
        )

        print(f"Point accuracy successfully generated at: {self.point_accuracy_path}")

    def convert_results_to_hex(self, contours=False, res=6) -> None:
        if contours:
            self.contour_path = os.path.join(
                self.output_geodatabase, f"{self.feature_name}_filledContours"
            )

            arcpy.ga.GALayerToContour(
                self.geostats_layer,
                "FILLED_CONTOUR",
                self.contour_path,
                "PRESENTATION",
                "GEOMETRIC_INTERVAL",
                20,
                [],
                None,
            )

        self._empty_tessellation_path = os.path.join(
            self.output_geodatabase, f"{self.feature_name}_h3_{res}_empty"
        )

        arcpy.management.GenerateTessellation(
            self._empty_tessellation_path,
            Extent=self.point_feature_class,
            Shape_Type="H3_HEXAGON",
            H3_Resolution=res
        )

        self.tessellation_path = os.path.join(
            self.output_geodatabase, f"{self.feature_name}_h3_{res}"
        )

        if contours:
            arcpy.gapro.SummarizeWithin(
                self.contour_path,
                self.tessellation_path,
                "POLYGON",
                summary_polygons=self._empty_tessellation_path,
                sum_shape="NO_SUMMARY",
                standard_summary_fields="Value_Max MEAN Count",
            )

        else:
            arcpy.gapro.SummarizeWithin(
                self.point_accuracy_path,
                self.tessellation_path,
                "POLYGON",
                summary_polygons=self._empty_tessellation_path,
                sum_shape="NO_SUMMARY",
                standard_summary_fields="Predicted MEAN Rate",
            )

        print(
            f"Data successfully aggregated to H3 hexagons at: {self.tessellation_path}"
        )

    def export_to_sde(self, sde_path: PathLike, dataset: str) -> None:
        if dataset == "TESSELLATION":
            input_fc = self.tessellation_path
            output_fc = os.path.join(sde_path, f"{self.feature_name}_h3")

        elif dataset == "POINT_ACCURACY":
            input_fc = self.point_accuracy_path
            output_fc = os.path.join(sde_path, f"{self.feature_name}_point_diff")

        else:
            if type(dataset) == str:
                raise ValueError(
                    "Param 'dataset' must be in ['TESSELLATION', 'POINT_ACCURACY']"
                )
            else:
                raise TypeError(
                    "Param 'dataset' must be of type string and value of ['TESSELLATION', 'POINT_ACCURACY']"
                )
        arcpy.conversion.ExportFeatures(input_fc, output_fc)