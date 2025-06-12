from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, isnan, isnull
from pyspark.sql.types import StringType
from pyspark.ml.feature import StringIndexer, VectorAssembler, StandardScaler
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml import Pipeline, PipelineModel

# 1. Initialize Spark session
spark = SparkSession.builder.appName("PipelineTraining").getOrCreate()

# 2. Read CSV data
df = spark.read.csv("../data/Thursday.csv", header=True, inferSchema=True)

# 3. Select relevant columns (same as in notebooks)
columns_to_keep = [
    "protocol",
    "src2dst_packets",
    "dst2src_packets",
    "src2dst_bytes",
    "dst2src_bytes",
    "bidirectional_duration_ms",
    "bidirectional_min_ps",
    "bidirectional_max_ps",
    "bidirectional_mean_ps",
    "bidirectional_stddev_ps",
    "src2dst_max_ps",
    "src2dst_min_ps",
    "src2dst_mean_ps",
    "src2dst_stddev_ps",
    "dst2src_max_ps",
    "dst2src_min_ps",
    "dst2src_mean_ps",
    "dst2src_stddev_ps",
    "bidirectional_mean_piat_ms",
    "bidirectional_stddev_piat_ms",
    "bidirectional_max_piat_ms",
    "bidirectional_min_piat_ms",
    "src2dst_mean_piat_ms",
    "src2dst_stddev_piat_ms",
    "src2dst_max_piat_ms",
    "src2dst_min_piat_ms",
    "dst2src_mean_piat_ms",
    "dst2src_stddev_piat_ms",
    "dst2src_max_piat_ms",
    "dst2src_min_piat_ms",
    "bidirectional_fin_packets",
    "bidirectional_syn_packets",
    "bidirectional_rst_packets",
    "bidirectional_psh_packets",
    "bidirectional_ack_packets",
    "bidirectional_urg_packets",
    "bidirectional_cwr_packets",
    "bidirectional_ece_packets",
    "src2dst_psh_packets",
    "dst2src_psh_packets",
    "src2dst_urg_packets",
    "dst2src_urg_packets",
    "label"
]
df = df.select([col(c) for c in columns_to_keep if c in df.columns])

# 4. Clean data: drop rows with any missing values
nan_condition = None
for c in df.columns:
    cond = isnull(col(c)) | isnan(col(c))
    nan_condition = cond if nan_condition is None else nan_condition | cond
df_clean = df.filter(~nan_condition) if nan_condition is not None else df

# 5. Encode label: BENIGN as 0, all others as 1 (ANOMALY)
if "label" in df_clean.columns:
    df_clean = df_clean.withColumn("label", when(col("label") == "BENIGN", "BENIGN").otherwise("ANOMALY"))

# 6. Encode categorical columns (except label)
categorical_cols = [field.name for field in df_clean.schema.fields if isinstance(field.dataType, StringType) and field.name != "label"]
numeric_cols = [field.name for field in df_clean.schema.fields if field.dataType.typeName() in ['integer', 'double', 'long', 'float']]

indexers = [StringIndexer(inputCol=col_name, outputCol=col_name + "_idx", handleInvalid="keep") for col_name in categorical_cols]
label_indexer = StringIndexer(inputCol="label", outputCol="label_idx", handleInvalid="keep")

# 7. Assemble features and normalize
feature_cols = [col + "_idx" for col in categorical_cols] + numeric_cols
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features_vec")
scaler = StandardScaler(inputCol="features_vec", outputCol="features_scaled")

# 8. Decision Tree Classifier
dt = DecisionTreeClassifier(featuresCol="features_scaled", labelCol="label_idx", seed=42)

# 9. Build pipeline
pipeline = Pipeline(stages=indexers + [label_indexer, assembler, scaler, dt])

# 10. Train pipeline
model = pipeline.fit(df_clean)

# 11. Save pipeline and model
pipeline_path = "../models/nfs2023_pipeline"
model_path = "../models/nfs2023_pipeline_model"
pipeline.write().overwrite().save(pipeline_path)
model.write().overwrite().save(model_path)

print("Pipeline and model saved.")
