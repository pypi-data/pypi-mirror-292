from SparkCleaner.Strategies.base import CleaningStrategy, DataFrame

class DropDuplicatesStrategy(CleaningStrategy):
    def clean(self, df: DataFrame) -> DataFrame:
        columns_to_check = [col for col in self.columns if col != "__index"]
        initial_count = df.count()
        df_cleaned = df.dropDuplicates(subset=columns_to_check)
        final_count = df_cleaned.count()
        
        if initial_count > final_count:
            df_with_duplicates = df.join(df_cleaned, on=["__index"], how='left_anti')
            duplicate_rows = df_with_duplicates.collect()
            for row in duplicate_rows:
                self.logger.log_error(row['__index'], self.columns, f"Duplicate row found: {row}")

        return df_cleaned