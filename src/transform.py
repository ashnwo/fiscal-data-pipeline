from pyspark.sql import SparkSession
from datetime import datetime  
from pyspark.sql import functions as sf
from pyspark.sql.types import DecimalType, ArrayType, StructType, StructField, DateType, IntegerType, StringType


spark = SparkSession.builder.appName("treasury_debt-transform").getOrCreate()

schema = StructType([ 
    StructField("data", 
                ArrayType(
                    StructType([
                        StructField("debt_held_public_amt", StringType()), 
                        StructField("intragov_hold_amt", StringType()), 
                        StructField("tot_pub_debt_out_amt", StringType()), 
                        StructField("record_date", DateType()), 
                        StructField("record_calendar_year", StringType()), 
                        StructField("record_calendar_month", StringType()), 
                        StructField("record_calendar_day", StringType()), 
                        StructField("record_calendar_quarter", StringType()), 
                        StructField("record_fiscal_year", StringType()), 
                        StructField("record_fiscal_quarter", StringType()), 
                        StructField("src_line_nbr", StringType())
                        ])
                    )
                )
            ])


print(spark.version)

# path = f'data/raw/debt_to_penny_{datetime.today().strftime("%Y%m%d")}/treasury_raw.json'

data = 'data/raw/debt_to_penny_20260714/treasury_raw.json'

# df = spark.read.json(data)
df = spark.read.json(data, schema=schema, mode="FAILFAST")

df = df.select(sf.explode('data').alias('d')).select('d.*')
df.printSchema()
df.show(5, truncate=True)

df_typed = (df
    # .cast = job will fail if cast fails. 
    .withColumn("debt_held_public_amt",  sf.col("debt_held_public_amt").cast("decimal(18,2)"))
    .withColumn("intragov_hold_amt",     sf.col("intragov_hold_amt").cast("decimal(18,2)"))
    .withColumn("tot_pub_debt_out_amt",  sf.col("tot_pub_debt_out_amt").cast("decimal(18,2)"))
    # .try_cast = a bad value will return null, job survives.
    .withColumn("record_calendar_year",    sf.col("record_calendar_year").try_cast("int"))
    .withColumn("record_calendar_month",   sf.col("record_calendar_month").try_cast("int"))
    .withColumn("record_calendar_day",     sf.col("record_calendar_day").try_cast("int"))
    .withColumn("record_calendar_quarter", sf.col("record_calendar_quarter").try_cast("int"))
    .withColumn("record_fiscal_year",      sf.col("record_fiscal_year").try_cast("int"))
    .withColumn("record_fiscal_quarter",  sf.col("record_fiscal_quarter").try_cast("int"))
)
df_typed.printSchema()


print(f"rows: {df_typed.count()}")

# Counts how many try_cast operations failed for the calendar date columns. # of nulls.
df_typed.select([sf.sum(sf.col(c).isNull().cast("int")).alias(c)
                 for c in ["record_calendar_year","record_calendar_month","record_calendar_day",
                           "record_calendar_quarter","record_fiscal_year","record_fiscal_quarter"]]).show()


df_typed.select(sf.min("record_date"), sf.max("record_date")).show() # checking record_date range.



