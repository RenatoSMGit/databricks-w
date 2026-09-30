from pyspark.sql import functions as F
from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

pedidos = spark.table('trusted_data_dev.comercial.pedidos')

df = pedidos.groupBy(F.to_date('dt_pedido').alias('dt_venda'), 'id_cliente').agg(
    F.count('id_pedido').alias('qt_pedidos'),
    F.sum('vl_total').cast('decimal(18,2)').alias('vl_vendas')
)

df = df.withColumn('sk_kpi', F.monotonically_increasing_id())

df.write.mode('overwrite').format('delta').option('overwriteSchema', 'true').saveAsTable('refined_data_dev.comercial.kpi_vendas_diarias')

print('Refined concluído.')
