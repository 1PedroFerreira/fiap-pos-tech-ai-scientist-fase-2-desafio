"""Silver: metas de alfabetização unificadas.

Consolida as três entidades de meta (Brasil, UF e Município) em um único
dataset com coluna de escopo, já tipado, para consumo pela camada Gold.
"""

from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="silver_metas",
    comment=(
        "Metas de alfabetização unificadas por escopo "
        "(brasil / uf / municipio), ano e meta percentual."
    ),
)
def silver_metas():
    brasil = (
        spark.read.table("bronze_meta_alfabetizacao_brasil")
        .select(
            F.lit("brasil").alias("escopo"),
            F.col("ano").cast("int").alias("ano"),
            F.lit(None).cast("string").alias("sigla_uf"),
            F.lit(None).cast("bigint").alias("id_municipio"),
            F.col("meta_pct").cast("double").alias("meta_pct"),
        )
    )

    uf = (
        spark.read.table("bronze_meta_alfabetizacao_uf")
        .select(
            F.lit("uf").alias("escopo"),
            F.col("ano").cast("int").alias("ano"),
            F.trim("sigla_uf").alias("sigla_uf"),
            F.lit(None).cast("bigint").alias("id_municipio"),
            F.col("meta_pct").cast("double").alias("meta_pct"),
        )
    )

    municipio = (
        spark.read.table("bronze_meta_alfabetizacao_municipio")
        .select(
            F.lit("municipio").alias("escopo"),
            F.col("ano").cast("int").alias("ano"),
            F.lit(None).cast("string").alias("sigla_uf"),
            F.col("id_municipio").cast("bigint").alias("id_municipio"),
            F.col("meta_pct").cast("double").alias("meta_pct"),
        )
    )

    return brasil.unionByName(uf).unionByName(municipio)
