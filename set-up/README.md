# Big Data Lab Deployment Guide

This guide explains how to deploy a Big Data lab environment with Apache Kafka, Apache Spark 3.4.2, Apache HDFS, and Python 3.8 using Docker Compose.

## Prerequisites
- Docker and Docker Compose installed on your system
- Linux OS (recommended)

## Directory Structure
```
code/                # Place your Python/Spark code here
set-up/
  docker-compose.yml
  Dockerfile.spark   # Custom Dockerfile for Spark with conda and Python 3.8
  hdfs/
    datanode/
    namenode/
```

## Deployment Steps

1. **Navigate to the setup directory:**
   ```bash
   cd set-up
   ```

2. **Build the custom Spark image:**
   ```bash
   docker-compose build
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

4. **Access Spark master container:**
   ```bash
   docker exec -it <container_id_or_name_of_spark-master> bash
   ```
   - The code directory is mounted at `/code` inside the container.
   - The Python 3.8 environment with `pyspark==3.4.2` and `kafka-python` is available.
   - **Navigate to your code directory inside the container:**
     ```bash
     cd /code
     ```

5. **Activate the Python environment (inside the container):**
   ```bash
   conda activate pyspark38
   ```

6. **Install additional Python packages with pip (inside the container and environment):**
   ```bash
   pip install <package-name>
   ```

7. **Run your Python or Spark jobs as needed.**

## How to connect from Spark master container to Hadoop Namenode

- Use the HDFS URI: `hdfs://namenode:9000/`
- The hostname `namenode` matches the service name in `docker-compose.yml` and is resolvable by all containers on the same Docker network.
- Example in PySpark:
  ```python
  df.write.csv("hdfs://namenode:9000/path/to/output")
  ```
- Make sure the Hadoop Namenode is running and accessible on port 9000.
- Both Spark and Hadoop services must be on the same Docker network (already configured in your `docker-compose.yml`).

## Update the Deployment

If you have changed `docker-compose.yml` or other configuration files, follow these steps to update your deployment:

1. **Rebuild images if needed (for example, if Dockerfile.spark changed):**
   ```bash
   docker-compose build
   ```

2. **Restart the services to apply changes:**
   ```bash
   docker-compose up -d
   ```

3. **(Optional) If you want to remove old containers and start fresh:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Notes
- Edit and develop your code on the host in the `code/` directory. It will be available inside the Spark containers at `/code`.
- HDFS web UI: http://localhost:9870
- Spark master web UI: http://localhost:8080
- Kafka broker: `kafka:9092` (from within containers)

---

For troubleshooting or further customization, edit the `docker-compose.yml` and `Dockerfile.spark` files as needed.
