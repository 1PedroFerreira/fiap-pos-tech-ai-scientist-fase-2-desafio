"""Gold: comparação da taxa de alfabetização real do Brasil versus a meta nacional.

Usa as entidades: dados de alunos (fato) e meta de alfabetização Brasil.
"""

from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="gold_alfabetizacao_brasil",
    comment="Taxa de alfabetização real por ano comparada à meta nacional.",
)
def gold_alfabetizacao_brasil():
    fatos = spark.read.table("silver_alunos").groupBy("ano").agg(
        F.count("*").alias("qtd_alunos"),
        F.round(F.avg(F.col("alfabetizado").cast("int")), 4).alias("pct_alfabetizados"),
    )

    metas = (
        spark.read.table("silver_metas")
        .where("escopo = 'brasil'")
        .select("ano", "meta_pct")
    )

    return (
        fatos.join(metas, "ano", "left")
        .withColumn(
            "atingimento_meta",
            F.round(F.col("pct_alfabetizados") - F.col("meta_pct"), 4),
        )
        .withColumn("meta_atingida", F.col("pct_alfabetizados") >= F.col("meta_pct"))
        .select(
            "ano",
            "qtd_alunos",
            "pct_alfabetizados",
            "meta_pct",
            "atingimento_meta",
            "meta_atingida",
        )
    )
