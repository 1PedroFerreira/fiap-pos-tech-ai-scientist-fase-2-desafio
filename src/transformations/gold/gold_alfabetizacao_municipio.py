"""Gold: comparação da taxa de alfabetização por município versus a meta municipal.

Usa as entidades: dados de alunos (fato), dimensão Município, dimensão UF
e meta por município.
"""

from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="gold_alfabetizacao_municipio",
    comment="Taxa de alfabetização real por município e ano comparada à meta municipal.",
)
def gold_alfabetizacao_municipio():
    fatos = (
        spark.read.table("silver_alunos")
        .groupBy("ano", "id_municipio", "sigla_uf")
        .agg(
            F.count("*").alias("qtd_alunos"),
            F.round(F.avg(F.col("alfabetizado").cast("int")), 4).alias("pct_alfabetizados"),
        )
    )

    metas = (
        spark.read.table("silver_metas")
        .where("escopo = 'municipio'")
        .select("ano", "id_municipio", "meta_pct")
    )

    dim_municipio = (
        spark.read.table("silver_municipio")
        .select("id_municipio", "nome_municipio", "sigla_uf")
    )

    dim_uf = spark.read.table("silver_uf").select("sigla_uf", "nome_uf", "regiao")

    return (
        fatos.join(metas, ["ano", "id_municipio"], "left")
        .join(dim_municipio, ["id_municipio", "sigla_uf"], "left")
        .join(dim_uf, "sigla_uf", "left")
        .withColumn(
            "atingimento_meta",
            F.round(F.col("pct_alfabetizados") - F.col("meta_pct"), 4),
        )
        .withColumn("meta_atingida", F.col("pct_alfabetizados") >= F.col("meta_pct"))
        .select(
            "ano",
            "id_municipio",
            "nome_municipio",
            "sigla_uf",
            "nome_uf",
            "regiao",
            "qtd_alunos",
            "pct_alfabetizados",
            "meta_pct",
            "atingimento_meta",
            "meta_atingida",
        )
    )
