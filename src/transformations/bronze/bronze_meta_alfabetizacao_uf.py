"""Bronze: metas de alfabetização por Unidade Federativa."""

from pyspark import pipelines as dp

VOLUME_PATH = "/Volumes/workspace/default/vol_avaliacao_alfabetizacao"


@dp.materialized_view(
    name="bronze_meta_alfabetizacao_uf",
    comment="Meta de alfabetização por UF e ano, ingerida em batch do volume.",
)
def bronze_meta_alfabetizacao_uf():
    return (
        spark.read.format("csv")
        .option("header", "true")
        .load(f"{VOLUME_PATH}/batch/meta_alfabetizacao_uf")
    )
