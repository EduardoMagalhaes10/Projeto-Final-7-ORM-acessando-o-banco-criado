"""
UFCA — Universidade Federal do Cariri
Disciplina: ADS0011 — Projeto de Banco de Dados
Semestre: 2025.2
Nome: Eduardo Magalhães · Matrícula:2025013209
operations/crud.py — Operações CRUD via ORM (sem SQL manual)

Parte 3 do projeto:
  CREATE  — inserir_novos_alunos()          → 3 novas Pessoas + Alunos
  READ    — listar_alunos()                 → paginado e ordenado
  UPDATE  — atualizar_cr_aluno()            → altera CR de um aluno
  DELETE  — remover_aluno()                 → remove Aluno + Pessoa (CASCADE)
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ..models import Aluno, Curso, HorarioTurma, Pessoa, Turma


# ─────────────────────────────────────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────────────────────────────────────

def inserir_novos_alunos(session: Session) -> List[Aluno]:
    """
    Insere 3 novas Pessoas + Alunos no banco via ORM.
    Retorna a lista dos Alunos criados.
    """
    novos = [
        {
            "nome":      "Hugo Cavalcante Barros",
            "email":     "hugo.barros@aluno.ufca.edu.br",
            "matricula": "2025013210",
            "cr":        None,
        },
        {
            "nome":      "Isabela Freitas Nunes",
            "email":     "isabela.nunes@aluno.ufca.edu.br",
            "matricula": "2025013211",
            "cr":        None,
        },
        {
            "nome":      "João Victor Melo",
            "email":     "joao.melo@aluno.ufca.edu.br",
            "matricula": "2025013212",
            "cr":        None,
        },
    ]

    criados: List[Aluno] = []
    for dados in novos:
        pessoa = Pessoa(nome=dados["nome"], email=dados["email"])
        session.add(pessoa)
        session.flush()  # obtém id_pessoa gerado antes do commit

        aluno = Aluno(
            id_aluno=pessoa.id_pessoa,
            matricula=dados["matricula"],
            cr=dados["cr"],
        )
        session.add(aluno)
        criados.append(aluno)

    session.commit()
    print(f"\n[CREATE] {len(criados)} alunos inseridos com sucesso.")
    for a in criados:
        session.refresh(a)
        print(f"  ↳ {a.pessoa.nome}  |  matrícula: {a.matricula}")
    return criados


# ─────────────────────────────────────────────────────────────────────────────
# READ  (paginado + ordenado)
# ─────────────────────────────────────────────────────────────────────────────

def listar_alunos(
    session: Session,
    pagina: int = 1,
    por_pagina: int = 5,
    ordenar_por: str = "matricula",
) -> List[Aluno]:
    """
    Lista alunos com paginação simples e ordenação dinâmica.
    ordenar_por aceita: 'matricula' | 'nome' | 'cr'
    """
    offset = (pagina - 1) * por_pagina

    query = session.query(Aluno).join(Aluno.pessoa)

    if ordenar_por == "nome":
        query = query.order_by(Pessoa.nome)
    elif ordenar_por == "cr":
        query = query.order_by(Aluno.cr.desc().nullslast())
    else:
        query = query.order_by(Aluno.matricula)

    alunos = query.offset(offset).limit(por_pagina).all()

    total = session.query(Aluno).count()
    print(
        f"\n[READ] Página {pagina} | {por_pagina} por página | "
        f"total de alunos: {total}"
    )
    for a in alunos:
        cr_fmt = f"{a.cr:.2f}" if a.cr is not None else "Sem CR"
        print(f"  [{a.matricula}] {a.pessoa.nome:<35} CR: {cr_fmt}")
    return alunos


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────────────────────────────────────

def atualizar_cr_aluno(
    session: Session,
    matricula: str,
    novo_cr: Decimal,
) -> Optional[Aluno]:
    """
    Atualiza o Coeficiente de Rendimento (CR) de um aluno pela matrícula.
    Retorna o Aluno atualizado ou None se não encontrado.
    """
    aluno = session.query(Aluno).filter(Aluno.matricula == matricula).first()
    if aluno is None:
        print(f"\n[UPDATE] Aluno com matrícula '{matricula}' não encontrado.")
        return None

    cr_anterior = aluno.cr
    aluno.cr = novo_cr
    session.commit()
    session.refresh(aluno)

    print(
        f"\n[UPDATE] CR de '{aluno.pessoa.nome}' atualizado: "
        f"{cr_anterior} → {aluno.cr}"
    )
    return aluno


# ─────────────────────────────────────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────────────────────────────────────

def remover_aluno(session: Session, matricula: str) -> bool:
    """
    Remove um Aluno (e a Pessoa associada via CASCADE).
    Retorna True se removido, False se não encontrado.
    Nota: falha com IntegrityError se o aluno possuir matrículas ativas
    (ON DELETE RESTRICT na tabela MATRICULAS — comportamento correto).
    """
    aluno = (
        session.query(Aluno)
        .join(Aluno.pessoa)
        .filter(Aluno.matricula == matricula)
        .first()
    )
    if aluno is None:
        print(f"\n[DELETE] Aluno '{matricula}' não encontrado.")
        return False

    nome = aluno.pessoa.nome
    # Remover a Pessoa dispara CASCADE para Aluno
    session.delete(aluno.pessoa)
    session.commit()
    print(f"\n[DELETE] Aluno '{nome}' (matrícula: {matricula}) removido com sucesso.")
    return True
