from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
from pyspark.sql.functions import from_json, col, lit, isnan, isnull, when
from pyspark.sql.types import StructType, StructField, DoubleType, StringType

# Define schema for incoming Kafka data (match columns_to_keep)
schema = StructType([
    StructField("protocol", DoubleType(), True),
    StructField("src2dst_packets", DoubleType(), True),
    StructField("dst2src_packets", DoubleType(), True),
    StructField("src2dst_bytes", DoubleType(), True),
    StructField("dst2src_bytes", DoubleType(), True),
    StructField("bidirectional_duration_ms", DoubleType(), True),
    StructField("bidirectional_min_ps", DoubleType(), True),
    StructField("bidirectional_max_ps", DoubleType(), True),
    StructField("bidirectional_mean_ps", DoubleType(), True),
    StructField("bidirectional_stddev_ps", DoubleType(), True),
    StructField("src2dst_max_ps", DoubleType(), True),
    StructField("src2dst_min_ps", DoubleType(), True),
    StructField("src2dst_mean_ps", DoubleType(), True),
    StructField("src2dst_stddev_ps", DoubleType(), True),
    StructField("dst2src_max_ps", DoubleType(), True),
    StructField("dst2src_min_ps", DoubleType(), True),
    StructField("dst2src_mean_ps", DoubleType(), True),
    StructField("dst2src_stddev_ps", DoubleType(), True),
    StructField("bidirectional_mean_piat_ms", DoubleType(), True),
    StructField("bidirectional_stddev_piat_ms", DoubleType(), True),
    StructField("bidirectional_max_piat_ms", DoubleType(), True),
    StructField("bidirectional_min_piat_ms", DoubleType(), True),
    StructField("src2dst_mean_piat_ms", DoubleType(), True),
    StructField("src2dst_stddev_piat_ms", DoubleType(), True),
    StructField("src2dst_max_piat_ms", DoubleType(), True),
    StructField("src2dst_min_piat_ms", DoubleType(), True),
    StructField("dst2src_mean_piat_ms", DoubleType(), True),
    StructField("dst2src_stddev_piat_ms", DoubleType(), True),
    StructField("dst2src_max_piat_ms", DoubleType(), True),
    StructField("dst2src_min_piat_ms", DoubleType(), True),
    StructField("bidirectional_fin_packets", DoubleType(), True),
    StructField("bidirectional_syn_packets", DoubleType(), True),
    StructField("bidirectional_rst_packets", DoubleType(), True),
    StructField("bidirectional_psh_packets", DoubleType(), True),
    StructField("bidirectional_ack_packets", DoubleType(), True),
    StructField("bidirectional_urg_packets", DoubleType(), True),
    StructField("bidirectional_cwr_packets", DoubleType(), True),
    StructField("bidirectional_ece_packets", DoubleType(), True),
    StructField("src2dst_psh_packets", DoubleType(), True),
    StructField("dst2src_psh_packets", DoubleType(), True),
    StructField("src2dst_urg_packets", DoubleType(), True),
    StructField("dst2src_urg_packets", DoubleType(), True),
    StructField("Label", StringType())
])

# Start Spark session with Kafka JARs configured
spark = SparkSession.builder \
    .appName("RealTimePrediction") \
    .config("spark.jars", "/opt/bitnami/spark/jars/spark-streaming-kafka-0-10-assembly_2.12-3.4.2.jar,\
            /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.4.2.jar, \
            /opt/bitnami/spark/jars/commons-pool2-2.11.1.jar") \
    .getOrCreate()

# Load trained pipeline model
model = PipelineModel.load("../models/nfs2023_pipeline_model")

# Read from Kafka topic
kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "network-flows")
    .option("startingOffsets", "latest")
    .load()
)

# Parse JSON value and extract fields using the defined schema
json_df = kafka_df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

# Fill missing values with defaults: protocol as -1, others as 0.0
fill_dict = {c: -1.0 if c == "protocol" else 0.0 for c in schema.fieldNames()}
json_df = json_df.fillna(fill_dict)

json_df = json_df.fillna({"label": "unknown"})

# Apply the pipeline model for prediction
predictions = model.transform(json_df)

# Write predictions to console (or to another sink as needed)
query = predictions.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .trigger(processingTime='2 seconds') \
    .start()

query.awaitTermination()
