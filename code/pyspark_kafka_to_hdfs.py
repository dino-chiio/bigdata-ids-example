from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

spark = SparkSession.builder \
    .appName("KafkaToHDFS") \
    .getOrCreate()

schema = StructType([
    StructField("id", IntegerType()),
    StructField("value", StringType())
])

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "test-topic") \
    .option("startingOffsets", "earliest") \
    .load()

json_df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

query = json_df.writeStream \
    .format("json") \
    .option("path", "hdfs://namenode:9000/user/spark/kafka_output") \
    .option("checkpointLocation", "/tmp/spark_checkpoint/kafka_to_hdfs") \
    .outputMode("append") \
    .start()

query.awaitTermination()
