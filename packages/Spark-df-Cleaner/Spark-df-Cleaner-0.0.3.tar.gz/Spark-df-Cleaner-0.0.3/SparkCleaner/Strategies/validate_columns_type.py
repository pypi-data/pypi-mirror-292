from SparkCleaner.Strategies.base import CleaningStrategy, DataFrame 
from pyspark.sql import DataFrame
from pyspark.sql.functions import when, lit, col
from pyspark.sql.types import DataType
from typing import List, Dict

class ValidateColumnTypesStrategy(CleaningStrategy):
    def __init__(self, columns: List[str], expected_types: Dict[str, DataType]):
        super().__init__(columns)
        self.expected_types = expected_types

    def clean(self, df: DataFrame) -> DataFrame:
        corrupted_rows_df = df
        for column in self.columns:
            if column in self.expected_types:
                expected_type = self.expected_types[column]
                corrupted_condition = col(column).cast(expected_type).isNull() & col(column).isNotNull()
                corrupted_rows_df = corrupted_rows_df.filter(corrupted_condition)
                mismatched_rows = corrupted_rows_df.collect()
                for row in mismatched_rows:
                    self.logger.log_error(row["__index"], column, f"Type mismatch in column '{column}'. "
                                                        f"Expected {expected_type}, got {type(row[column])}.")

                df = df.withColumn(column, when(corrupted_condition, lit(None))
                                   .otherwise(col(column).cast(expected_type)))
        return df

