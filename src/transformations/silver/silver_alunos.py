"""Silver: avaliações de alunos deduplicadas, validadas e enriquecidas.

- Deduplicação por id_aluno + ano (janela de watermark em data_avaliacao);
- Expectations descartam registros inválidos (chaves nulas, notas negativas,
  nível de escrita fora de 1-4);
- Deriva a flag "alfabetizado" (níveis de escrita 3 e 4).
"""

from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.table(
    name="silver_alunos",
    comment=(
        "Avaliações por aluno deduplicadas e validadas, com flag de alfabetização "
        "(níveis de escrita 3 e 4)."
    ),
)
@dp.expect_all_or_drop(
    {
        "id_aluno presente": "id_aluno IS NOT NULL",
        "chave geográfica presente": "id_municipio IS NOT NULL AND sigla_uf IS NOT NULL",
        "ano válido": "ano IS NOT NULL AND ano >= 2020",
        "proficiências não negativas": (
            "proficiencia_leitura >= 0 AND proficiencia_escrita >= 0 "
            "AND proficiencia_matematica >= 0"
        ),
        "nível de escrita entre 1 e 4": "nivel_escrita BETWEEN 1 AND 4",
    }
)
def silver_alunos():
    return (
        spark.readStream.table("bronze_alunos")
        .withWatermark("data_avaliacao", "30 days")
        .dropDuplicatesWithinWatermark(["id_aluno", "ano"])
        .withColumn("alfabetizado", F.col("nivel_escrita") >= 3)
        .select(
            "ano",
            "id_aluno",
            "id_escola",
            "id_municipio",
            "sigla_uf",
            "rede",
            "serie",
            "idade",
            "proficiencia_leitura",
            "proficiencia_escrita",
            "proficiencia_matematica",
            "nivel_escrita",
            "alfabetizado",
            "data_avaliacao",
        )
    )
