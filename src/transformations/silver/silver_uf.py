"""Silver: dimensão UF normalizada."""

from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="silver_uf",
    comment="Dimensão UF normalizada: sigla, nome e região sem espaços extras.",
)
def silver_uf():
    return spark.read.table("bronze_uf").select(
        F.trim("sigla_uf").alias("sigla_uf"),
        F.trim("nome_uf").alias("nome_uf"),
        F.trim("regiao").alias("regiao"),
    )
