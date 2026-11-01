"""Bronze: dimensão de Unidades Federativas (UF)."""

from pyspark import pipelines as dp

VOLUME_PATH = "/Volumes/workspace/default/vol_avaliacao_alfabetizacao"


@dp.materialized_view(
    name="bronze_uf",
    comment="Dimensão UF: sigla, nome e região, ingerida em batch do volume.",
)
def bronze_uf():
    return (
        spark.read.format("csv")
        .option("header", "true")
        .load(f"{VOLUME_PATH}/batch/uf")
    )
