from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.getActiveSession()

path = '/Volumes/landing_data_dev/comercial/clientes/'

df = spark.read.option('header', True).option('inferSchema', True).csv(path)
df = df.withColumn('_ingested_at', F.current_timestamp())

df.write.mode('append').format('delta').saveAsTable('raw_data_dev.comercial.clientes')

print('Arquivo de clientes persistido em raw_data_dev.comercial.clientes')
