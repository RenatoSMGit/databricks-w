from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

df = spark.table('trusted_data_dev.comercial.produtos')

df.write.mode('overwrite').format('delta').saveAsTable('curated_data_dev.comercial.dim_produto')

print('Dimensão de produtos criada em curated_data_dev.comercial.dim_produto')
