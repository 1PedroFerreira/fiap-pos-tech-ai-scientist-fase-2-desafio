"""Silver: dimensão Município normalizada."""

from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="silver_municipio",
    comment="Dimensão Município normalizada: código IBGE, nome e UF.",
)
def silver_municipio():
    return spark.read.table("bronze_municipio").select(
        F.col("id_municipio").cast("bigint").alias("id_municipio"),
        F.trim("nome_municipio").alias("nome_municipio"),
        F.trim("sigla_uf").alias("sigla_uf"),
    )
