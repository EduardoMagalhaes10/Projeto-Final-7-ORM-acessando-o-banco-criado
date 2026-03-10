"""
main.py — Ponto de entrada do projeto ORM
Sistema de Gestão Acadêmica
UFCA — Universidade Federal do Cariri
Disciplina: ADS0011 — Projeto de Banco de Dados
Semestre: 2025.2
Nome: Eduardo Magalhães · Matrícula:2025013209

Executa em sequência:
  1. Testa a conexão com o banco
  2. CRUD via ORM (Parte 3)
  3. Consultas com relacionamento (Parte 4)
"""

from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError

from database import get_session, engine
from operations.crud import (
    inserir_novos_alunos,
    listar_alunos,
    atualizar_cr_aluno,
    remover_aluno,
)
from queries.consultas import (
    listar_matriculas_ativas,
    cursos_e_pre_requisitos,
    top_alunos_por_cr,
    aprovados_por_disciplina,
)


def testar_conexao() -> bool:
    """Verifica se a conexão com o PostgreSQL está funcionando."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            versao = result.scalar()
        print("=" * 70)
        print("  SISTEMA DE GESTÃO ACADÊMICA — ORM com SQLAlchemy")
        print("=" * 70)
        versao_str = versao[:50] if versao else "Versão desconhecida"
        print(f"  Conexão OK  ✔  {versao_str}")
        return True
    except OperationalError as exc:
        print(f"\n  [ERRO] Não foi possível conectar ao banco:\n  {exc}")
        print("\n  Verifique as variáveis no arquivo .env e tente novamente.")
        return False


def main() -> None:
    if not testar_conexao():
        return

    session = get_session()

    try:
        # ── PARTE 3: CRUD ─────────────────────────────────────────────────────
        print("\n" + "─" * 70)
        print("  PARTE 3 — CRUD VIA ORM")
        print("─" * 70)

        # CREATE — 3 novos alunos
        novos_alunos = inserir_novos_alunos(session)
        matricula_novo = novos_alunos[0].matricula   # usado para UPDATE
        matricula_del  = novos_alunos[2].matricula   # usado para DELETE

        # READ — lista paginada, ordenada por matrícula
        listar_alunos(session, pagina=1, por_pagina=5, ordenar_por="matricula")

        # UPDATE — atualiza CR do primeiro aluno inserido
        atualizar_cr_aluno(session, matricula=matricula_novo, novo_cr=Decimal("7.85"))

        # DELETE — remove o terceiro aluno inserido (sem matrículas → OK)
        remover_aluno(session, matricula=matricula_del)

        # Exibe lista final para confirmar UPDATE e DELETE
        print()
        listar_alunos(session, pagina=1, por_pagina=5, ordenar_por="cr")

        # ── PARTE 4: CONSULTAS COM RELACIONAMENTO ─────────────────────────────
        print("\n" + "─" * 70)
        print("  PARTE 4 — CONSULTAS COM RELACIONAMENTO")
        print("─" * 70)

        listar_matriculas_ativas(session)   # JOIN 1-N / N-1
        cursos_e_pre_requisitos(session)    # JOIN N-N
        top_alunos_por_cr(session, limite=5)  # FILTRO + ORDENAÇÃO
        aprovados_por_disciplina(session)   # AGREGAÇÃO bônus

        print("\n" + "=" * 70)
        print("  Execução concluída com sucesso ✔")
        print("=" * 70)

    except IntegrityError as exc:
        session.rollback()
        print(f"\n[ERRO DE INTEGRIDADE] {exc.orig}")
    except Exception as exc:
        session.rollback()
        print(f"\n[ERRO INESPERADO] {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
