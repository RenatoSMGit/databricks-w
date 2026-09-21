from pyspark.sql import functions as F
from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

pedidos = spark.table('trusted_data_dev.comercial.pedidos')

df = pedidos.select(
    'id_pedido',
    'id_cliente',
    F.col('dt_pedido').alias('dt_pedido'),
    'vl_total',
    F.when(F.col('status_pedido') == 'PAGO', F.col('vl_total')).otherwise(0).alias('vl_liquido')
)

df = df.withColumn('sk_venda', F.monotonically_increasing_id())

df.write.mode('merge').format('delta').saveAsTable('curated_data_dev.comercial.fato_vendas')

print('Curated concluído.')
