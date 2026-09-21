from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

df = spark.table('trusted_data_dev.comercial.clientes')

df.write.mode('overwrite').format('delta').saveAsTable('curated_data_dev.comercial.dim_cliente')

print('Dimensão de clientes criada em curated_data_dev.comercial.dim_cliente')
