"""Bronze: metas nacionais de alfabetização."""

from pyspark import pipelines as dp

VOLUME_PATH = "/Volumes/workspace/default/vol_avaliacao_alfabetizacao"


@dp.materialized_view(
    name="bronze_meta_alfabetizacao_brasil",
    comment="Meta de alfabetização do Brasil por ano, ingerida em batch do volume.",
)
def bronze_meta_alfabetizacao_brasil():
    return (
        spark.read.format("csv")
        .option("header", "true")
        .load(f"{VOLUME_PATH}/batch/meta_alfabetizacao_brasil")
    )
