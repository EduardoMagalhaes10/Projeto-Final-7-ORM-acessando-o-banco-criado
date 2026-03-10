"""
UFCA — Universidade Federal do Cariri
Disciplina: ADS0011 — Projeto de Banco de Dados
Semestre: 2025.2
Nome: Eduardo Magalhães · Matrícula:2025013209
queries/consultas.py — Consultas com relacionamento (equivalente a JOIN) via ORM

Parte 4 do projeto — 3 consultas obrigatórias:
  1. [JOIN] listar_matriculas_ativas()     → alunos cursando com nome do curso
  2. [JOIN] cursos_e_pre_requisitos()      → cursos + seus pré-requisitos
  3. [FILTRO + ORDEM] top_alunos_por_cr()  → alunos com CR definido, decrescente
"""

from decimal import Decimal
from typing import List, Tuple

from sqlalchemy import func, and_
from sqlalchemy.orm import Session, joinedload

from models import Aluno, Curso, Matricula, Pessoa, Turma, pre_requisitos_table


# ─────────────────────────────────────────────────────────────────────────────
# Consulta 1 — JOIN: matrículas ativas com dados do aluno e do curso
# Equivale à Consulta 3 do script SQL original
# ─────────────────────────────────────────────────────────────────────────────

def listar_matriculas_ativas(session: Session) -> List[Matricula]:
    """
    Retorna todas as matrículas com situação 'CURSANDO',
    carregando em uma única query os dados de Aluno, Pessoa, Turma e Curso.
    """
    matriculas = (
        session.query(Matricula)
        .join(Matricula.aluno)               # JOIN alunos
        .join(Aluno.pessoa)                  # JOIN pessoas
        .join(Matricula.turma)               # JOIN turmas
        .join(Turma.curso)                   # JOIN cursos
        .filter(Matricula.situacao == "CURSANDO")
        .options(
            joinedload(Matricula.aluno).joinedload(Aluno.pessoa),
            joinedload(Matricula.turma).joinedload(Turma.curso),
        )
        .order_by(Pessoa.nome, Curso.nome)
        .all()
    )

    print("\n[CONSULTA 1 — JOIN] Matrículas ativas (CURSANDO):")
    print(f"  {'Aluno':<35} {'Matrícula':<15} {'Disciplina':<35} {'Período':<10} {'Freq.'}")
    print("  " + "─" * 105)
    for m in matriculas:
        freq = f"{m.frequencia:.1f}%" if m.frequencia is not None else "N/A"
        print(
            f"  {m.aluno.pessoa.nome:<35} "
            f"{m.aluno.matricula:<15} "
            f"{m.turma.curso.nome:<35} "
            f"{m.turma.periodo:<10} "
            f"{freq}"
        )
    return matriculas


# ─────────────────────────────────────────────────────────────────────────────
# Consulta 2 — JOIN N:N: cursos com seus pré-requisitos
# Equivale à Consulta 4 do script SQL original
# ─────────────────────────────────────────────────────────────────────────────

def cursos_e_pre_requisitos(session: Session) -> List[Curso]:
    """
    Lista todos os cursos junto com seus pré-requisitos
    usando o relacionamento N:N mapeado em Curso.pre_requisitos.
    """
    cursos = (
        session.query(Curso)
        .options(joinedload(Curso.pre_requisitos))
        .order_by(Curso.codigo)
        .all()
    )

    print("\n[CONSULTA 2 — JOIN N:N] Cursos e pré-requisitos:")
    print(f"  {'Código':<12} {'Disciplina':<40} Pré-requisitos")
    print("  " + "─" * 85)
    for c in cursos:
        pre = ", ".join(p.codigo for p in c.pre_requisitos) or "Nenhum"
        print(f"  {c.codigo:<12} {c.nome:<40} {pre}")
    return cursos


# ─────────────────────────────────────────────────────────────────────────────
# Consulta 3 — FILTRO + ORDENAÇÃO: top alunos por CR (apenas com CR definido)
# ─────────────────────────────────────────────────────────────────────────────

def top_alunos_por_cr(session: Session, limite: int = 5) -> List[Aluno]:
    """
    Retorna os 'limite' alunos com maior CR (excluindo alunos sem CR definido),
    ordenados de forma decrescente.
    Filtro:  cr IS NOT NULL
    Ordem:   cr DESC
    """
    alunos = (
        session.query(Aluno)
        .join(Aluno.pessoa)
        .filter(Aluno.cr.isnot(None))
        .order_by(Aluno.cr.desc())
        .limit(limite)
        .all()
    )

    print(f"\n[CONSULTA 3 — FILTRO + ORDEM] Top {limite} alunos por CR:")
    print(f"  {'Pos.':<6} {'Nome':<35} {'Matrícula':<15} {'CR'}")
    print("  " + "─" * 65)
    for pos, a in enumerate(alunos, start=1):
        print(f"  {pos:<6} {a.pessoa.nome:<35} {a.matricula:<15} {a.cr:.2f}")
    return alunos


# ─────────────────────────────────────────────────────────────────────────────
# Consulta BÔNUS — Agregação por relacionamento: aprovados por disciplina
# Equivale à Consulta 7 do script SQL original
# ─────────────────────────────────────────────────────────────────────────────

def aprovados_por_disciplina(session: Session) -> List[Tuple]:
    """
    Conta aprovados e calcula média de nota agrupado por disciplina.
    Usa agregação via ORM (func.count / func.avg).
    """
    resultados = (
        session.query(
            Curso.nome.label("disciplina"),
            func.count(Matricula.id_matricula).label("total_aprovados"),
            func.round(func.avg(Matricula.nota_final), 2).label("media"),
        )
        .join(Turma, Turma.id_curso == Curso.id_curso)
        .join(Matricula, Matricula.id_turma == Turma.id_turma)
        .filter(
            and_(
                Matricula.situacao == "APROVADO",
                Matricula.nota_final >= Decimal("7.0"),
            )
        )
        .group_by(Curso.nome)
        .order_by(func.avg(Matricula.nota_final).desc())
        .all()
    )

    print("\n[CONSULTA BÔNUS — AGREGAÇÃO] Aprovados por disciplina:")
    print(f"  {'Disciplina':<40} {'Aprovados':>10} {'Média':>8}")
    print("  " + "─" * 62)
    for r in resultados:
        print(f"  {r.disciplina:<40} {r.total_aprovados:>10} {float(r.media):>8.2f}")
    return resultados
