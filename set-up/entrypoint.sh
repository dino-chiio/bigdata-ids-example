#!/bin/bash
set -e

if [ "$SPARK_MODE" = "master" ]; then
  /opt/bitnami/scripts/spark/entrypoint.sh /opt/bitnami/scripts/spark/run.sh &
  # Wait a bit to ensure Spark master starts before Jupyter
  sleep 5
  cd /code
  exec /opt/conda/bin/conda run -n pyspark38 jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --notebook-dir=/code
elif [ "$SPARK_MODE" = "worker" ]; then
  exec /opt/bitnami/scripts/spark/entrypoint.sh /opt/bitnami/scripts/spark/run.sh
else
  echo "Unknown SPARK_MODE: $SPARK_MODE"
  exit 1
fi
