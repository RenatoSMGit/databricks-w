from pyspark.sql import functions as F
from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

df = spark.table('raw_data_dev.comercial.clientes')
df = df.filter(F.col('id_cliente').isNotNull())
df = df.withColumn('nm_cliente', F.initcap(F.trim(F.col('nm_cliente'))))
df = df.withColumn('sk_cliente', F.monotonically_increasing_id())

df.write.mode('overwrite').format('delta').saveAsTable('trusted_data_dev.comercial.clientes')

print('Tabela trusted_data_dev.comercial.clientes criada com sucesso...')
