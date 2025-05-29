from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SimpleTest").getOrCreate()

data = [("Alice", 1), ("Bob", 2), ("Cathy", 3)]
df = spark.createDataFrame(data, ["name", "id"])

df.show()

# Write DataFrame to HDFS as CSV
df.write.mode("overwrite").csv("hdfs://namenode:9000/user/spark/pyspark_example_output")

spark.stop()
