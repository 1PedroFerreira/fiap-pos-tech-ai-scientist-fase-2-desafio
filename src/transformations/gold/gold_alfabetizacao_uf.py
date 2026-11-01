"""Gold: comparação da taxa de alfabetização por UF versus a meta da UF.

Usa as entidades: dados de alunos (fato), dimensão UF e meta por UF.
"""

from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="gold_alfabetizacao_uf",
    comment="Taxa de alfabetização real por UF e ano comparada à meta estadual.",
)
def gold_alfabetizacao_uf():
    fatos = (
        spark.read.table("silver_alunos")
        .groupBy("ano", "sigla_uf")
        .agg(
            F.count("*").alias("qtd_alunos"),
            F.round(F.avg(F.col("alfabetizado").cast("int")), 4).alias("pct_alfabetizados"),
        )
    )

    metas = (
        spark.read.table("silver_metas")
        .where("escopo = 'uf'")
        .select("ano", "sigla_uf", "meta_pct")
    )

    dim_uf = spark.read.table("silver_uf").select("sigla_uf", "nome_uf", "regiao")

    return (
        fatos.join(metas, ["ano", "sigla_uf"], "left")
        .join(dim_uf, "sigla_uf", "left")
        .withColumn(
            "atingimento_meta",
            F.round(F.col("pct_alfabetizados") - F.col("meta_pct"), 4),
        )
        .withColumn("meta_atingida", F.col("pct_alfabetizados") >= F.col("meta_pct"))
        .select(
            "ano",
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
