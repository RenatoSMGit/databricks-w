from pyspark.sql import functions as F
from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

df = spark.table('raw_data_dev.comercial.produtos')
df = df.filter(F.col('id_produto').isNotNull())
df = df.filter(F.col('vl_unitario') > 0)
df = df.withColumn('sk_produto', F.monotonically_increasing_id())

df.write.mode('overwrite').format('delta').saveAsTable('trusted_data_dev.comercial.produtos')

print('Tabela trusted_data_dev.comercial.produtos criada com sucesso.')
