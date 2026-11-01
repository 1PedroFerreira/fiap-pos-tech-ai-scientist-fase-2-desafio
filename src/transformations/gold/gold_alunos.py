"""Gold: dados por aluno enriquecidos.

Usa as entidades: dados de alunos (fato), dimensão Município e dimensão UF.
"""

from pyspark import pipelines as dp


@dp.materialized_view(
    name="gold_alunos",
    comment="Avaliações por aluno com nome de município e UF, prontas para análise.",
)
def gold_alunos():
    alunos = spark.read.table("silver_alunos")

    dim_municipio = (
        spark.read.table("silver_municipio")
        .select("id_municipio", "nome_municipio")
    )

    dim_uf = spark.read.table("silver_uf").select("sigla_uf", "nome_uf", "regiao")

    return (
        alunos.join(dim_municipio, "id_municipio", "left")
        .join(dim_uf, "sigla_uf", "left")
        .select(
            "ano",
            "id_aluno",
            "id_escola",
            "id_municipio",
            "nome_municipio",
            "sigla_uf",
            "nome_uf",
            "regiao",
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
