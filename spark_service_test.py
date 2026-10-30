from app.services.spark_service import get_spark_analytics

result = get_spark_analytics()

print("Spark analytics received by Flask:")
print(result)