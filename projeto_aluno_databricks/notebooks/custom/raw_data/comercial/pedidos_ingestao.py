from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

# Exemplo de leitura de arquivos em landing
landing_path = '/Volumes/landing_data_dev/comercial/pedidos/'

df = spark.read.option('header', True).csv(landing_path)

df = df.withColumn('_ingested_at', F.current_timestamp())

df.write.mode('append').format('delta').saveAsTable('raw_data_dev.comercial.pedidos')

print('Ingestão concluída para raw_data_dev.comercial.pedidos')
