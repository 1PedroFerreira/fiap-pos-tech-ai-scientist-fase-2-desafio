"""Bronze: avaliações de alfabetização por aluno.

Combina ingestão batch (backfill único do histórico 2022-2024) e ingestão
streaming (Auto Loader na pasta de novos arquivos) em uma única streaming table.
"""

from pyspark import pipelines as dp
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

VOLUME_PATH = "/Volumes/workspace/default/vol_avaliacao_alfabetizacao"

ALUNOS_SCHEMA = StructType(
    [
        StructField("ano", IntegerType(), True),
        StructField("id_aluno", StringType(), True),
        StructField("id_escola", StringType(), True),
        StructField("id_municipio", LongType(), True),
        StructField("sigla_uf", StringType(), True),
        StructField("rede", StringType(), True),
        StructField("serie", IntegerType(), True),
        StructField("idade", IntegerType(), True),
        StructField("proficiencia_leitura", DoubleType(), True),
        StructField("proficiencia_escrita", DoubleType(), True),
        StructField("proficiencia_matematica", DoubleType(), True),
        StructField("nivel_escrita", IntegerType(), True),
        StructField("data_avaliacao", TimestampType(), True),
    ]
)

dp.create_streaming_table(
    name="bronze_alunos",
    comment=(
        "Avaliações de alfabetização por aluno: histórico 2022-2024 (batch) "
        "e novos arquivos em streaming via Auto Loader."
    ),
)


@dp.append_flow(
    target="bronze_alunos",
    name="alunos_streaming",
    comment="Streaming: novos arquivos de avaliações chegam na pasta e são processados pelo Auto Loader.",
)
def alunos_streaming():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .schema(ALUNOS_SCHEMA)
        .load(f"{VOLUME_PATH}/streaming/alunos")
    )


@dp.append_flow(
    target="bronze_alunos",
    name="alunos_backfill_historico",
    once=True,
    comment="Backfill batch único: carrega o histórico de avaliações 2022-2024 do volume.",
)
def alunos_backfill_historico():
    return (
        spark.read.format("csv")
        .option("header", "true")
        .schema(ALUNOS_SCHEMA)
        .load(f"{VOLUME_PATH}/batch/alunos_historico")
    )
