from pyspark.sql import SparkSession
from datetime import datetime  
from pyspark.sql import functions as sf
from pyspark.sql.types import DecimalType, ArrayType, StructType, StructField, DateType, IntegerType, StringType


# spark = SparkSession.builder.appName("treasury_debt-transform").getOrCreate()

# Grabbing JAR packages at session start-up. 
def transform(input_uri):
    spark = SparkSession.builder.appName("treasury_debt-transform").config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.4.2").getOrCreate()

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

    schema_flat = StructType(
        [
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
        ]
    )


    print(spark.version)

    # data_local_path = f'data/raw/debt_to_penny_{datetime.today().strftime("%Y%m%d")}/treasury_raw.json'

    # data_local_path = 'data/raw/debt_to_penny_20260714/treasury_raw.json'

    data = input_uri or "s3a://treasury-raw-an-2026/raw/us_treasury/debt_to_penny/year=2026/month=07/day=04/"

    df = spark.read.json(data, schema=schema_flat, mode="FAILFAST", multiLine=True)


    # df = df.select(sf.explode('data').alias('d')).select('d.*')

    print(df.count())
    df.printSchema()
    df.show(5, truncate=True)

    # Investigating _amt null count -> determined it was apart of the source data, values were not tracked in that date range.

    # tot_pub_debt_out_amt_null = df.filter(sf.col("tot_pub_debt_out_amt") == "null").count()
    # intragov_hold_amt_null = df.filter(sf.col("intragov_hold_amt") == "null").count()
    # debt_held_public_amt_null = df.filter(sf.col("debt_held_public_amt") == "null").count()
    # print(tot_pub_debt_out_amt_null)
    # print(intragov_hold_amt_null)
    # print(debt_held_public_amt_null)

    # null_range = df.filter(sf.col("debt_held_public_amt") == "null") \
    #   .agg(sf.min("record_date"), sf.max("record_date")) \
    #   .show()

    # print(null_range)

    amt_cols = ["debt_held_public_amt", "intragov_hold_amt", "tot_pub_debt_out_amt"]

    for c in amt_cols:
        df = df.withColumn(c, sf.when(sf.col(c) == 'null', sf.lit(None)).otherwise(sf.col(c)))


    # Data Typing 
    df_typed = (df
        # .cast = job will fail loudly if cast fails. 
        .withColumn("debt_held_public_amt",  sf.col("debt_held_public_amt").cast("decimal(18,2)"))
        .withColumn("intragov_hold_amt",     sf.col("intragov_hold_amt").cast("decimal(18,2)"))
        .withColumn("tot_pub_debt_out_amt",  sf.col("tot_pub_debt_out_amt").cast("decimal(18,2)"))
        # .try_cast = a bad value will return null, but job survives.
        .withColumn("record_calendar_year",    sf.col("record_calendar_year").try_cast("int"))
        .withColumn("record_calendar_month",   sf.col("record_calendar_month").try_cast("int"))
        .withColumn("record_calendar_day",     sf.col("record_calendar_day").try_cast("int"))
        .withColumn("record_calendar_quarter", sf.col("record_calendar_quarter").try_cast("int"))
        .withColumn("record_fiscal_year",      sf.col("record_fiscal_year").try_cast("int"))
        .withColumn("record_fiscal_quarter",  sf.col("record_fiscal_quarter").try_cast("int"))
    )
    df_typed.printSchema()


    print(f"rows: {df_typed.count()}")

    # Extracting year, month, and day from record_date
    df_typed = (df_typed
                .withColumn("year", sf.year(sf.col("record_date")))
                .withColumn("month", sf.month(sf.col("record_date")))
                .withColumn("day", sf.day(sf.col("record_date")))
    )

    df_typed.printSchema()

    # Counts how many try_cast operations failed for the calendar date columns. # of nulls.
    df_typed.select([sf.sum(sf.col(c).isNull().cast("int")).alias(c)
                    for c in ["record_calendar_year","record_calendar_month","record_calendar_day",
                            "record_calendar_quarter","record_fiscal_year","record_fiscal_quarter"]]).show()


    df_typed.select(sf.min("record_date"), sf.max("record_date")).show() # checking record_date range.



    # Parquet Write and Check
    # df_typed.write.mode("overwrite").parquet("data/bronze/debt/")

    # reloaded = spark.read.parquet("data/bronze/debt/")
    # reloaded.printSchema()

    df_typed.printSchema()

    df_typed.select("record_date", "year", "month", "day").show(5, truncate=False)

    s3 = "s3a://treasury-raw-an-2026/bronze"

    print('input: ', df_typed.count())

    # df_typed.write.mode("overwrite").parquet(s3)


    # df_typed.write.partitionBy("year","month","day").mode("overwrite").parquet(s3)

    # reloaded = spark.read.parquet(s3)
    # reloaded.printSchema()

