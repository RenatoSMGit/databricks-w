from pyspark.sql import functions as F
from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

df = spark.table('raw_data_dev.comercial.pedidos')

df = df.withColumn('dt_pedido', F.to_date('dt_pedido'))
df = df.withColumn('vl_total', F.col('vl_total').cast('decimal(12,2)'))
df = df.withColumn('status_pedido', F.upper(F.trim(F.col('status'))))
df = df.filter(F.col('id_pedido').isNotNull())

df.write.mode('overwrite').format('delta').option('overwriteSchema', 'true').saveAsTable('trusted_data_dev.comercial.pedidos')

print('Pipeline Trusted concluído.')
