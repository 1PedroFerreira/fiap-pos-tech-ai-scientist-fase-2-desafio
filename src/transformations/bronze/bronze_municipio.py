"""Bronze: dimensão de Municípios."""

from pyspark import pipelines as dp

VOLUME_PATH = "/Volumes/workspace/default/vol_avaliacao_alfabetizacao"


@dp.materialized_view(
    name="bronze_municipio",
    comment="Dimensão Município: código IBGE, nome e UF, ingerida em batch do volume.",
)
def bronze_municipio():
    return (
        spark.read.format("csv")
        .option("header", "true")
        .load(f"{VOLUME_PATH}/batch/municipio")
    )
