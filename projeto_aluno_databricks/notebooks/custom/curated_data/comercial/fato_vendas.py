from pyspark.sql import functions as F
from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

pedidos = spark.table('trusted_data_dev.comercial.pedidos')
valor_total = F.col('vl_total').cast('decimal(18,2)')

df = pedidos.select(
    'id_pedido',
    'id_cliente',
    F.col('dt_pedido').alias('dt_pedido'),
    valor_total.alias('vl_total'),
    F.when(F.col('status_pedido') == 'PAGO', valor_total)
    .otherwise(F.lit(0).cast('decimal(18,2)'))
    .alias('vl_liquido')
)

df = df.withColumn('sk_venda', F.monotonically_increasing_id())

df.write.mode('overwrite').format('delta').option('overwriteSchema', 'true').saveAsTable('curated_data_dev.comercial.fato_vendas')

print('Curated concluído.')
