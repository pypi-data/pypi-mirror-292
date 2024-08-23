from SparkCleaner.Strategies.base import CleaningStrategy
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import row_number,lit
from pyspark.sql.window import Window
import json

class CleaningPipeline:
    def __init__(self):
        self.strategies = []
        self.report = {}
        self.df = None

    def add_strategy(self, strategy: CleaningStrategy | list[CleaningStrategy]):
        if type(strategy) == list:
            [self.strategies.append(s) for s in strategy]
        elif isinstance(strategy, CleaningStrategy):
            self.strategies.append(strategy)

    def set_dataframe(self, df: DataFrame):
        self.df = df.withColumn('__index', row_number().over(
                Window().orderBy(lit('A'))
                ))

    def run(self) -> DataFrame:
        if self.df is None:
            raise ValueError("DataFrame has not been set.")
        
        for strategy in self.strategies:
            self.df = strategy.clean(self.df)
            self.report[strategy.whoami()] = strategy.get_report()
        
        return self.df.drop('__index')

    def get_report(self)-> str:
        if self.report:
            return json.dumps(self.report, indent=4)
        else:
            return json.dumps([{}], indent=4)
