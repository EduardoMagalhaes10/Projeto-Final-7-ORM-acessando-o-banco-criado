"""
UFCA — Universidade Federal do Cariri
Disciplina: ADS0011 — Projeto de Banco de Dados
Semestre: 2025.2
Nome: Eduardo Magalhães · Matrícula:2025013209
models/__init__.py — Mapeamento ORM das tabelas do Sistema de Gestão Acadêmica

Tabelas mapeadas:
  PESSOAS         → Pessoa
  ALUNOS          → Aluno          (1:1  com Pessoa)
  CURSOS          → Curso
  PRE_REQUISITOS  → tabela assoc.  (N:N  entre Curso)
  TURMAS          → Turma          (N:1  com Curso)
  HORARIOS_TURMA  → HorarioTurma   (N:1  com Turma)
  MATRICULAS      → Matricula      (N:1  com Aluno; N:1 com Turma)

Relacionamentos implementados (≥ 2 exigidos):
  • 1-N  Curso      → Turma        (Curso.turmas / Turma.curso)
  • 1-N  Turma      → HorarioTurma (Turma.horarios / HorarioTurma.turma)
  • 1-N  Aluno      → Matricula    (Aluno.matriculas / Matricula.aluno)
  • N-N  Curso      ↔ Curso        (Curso.pre_requisitos via PRE_REQUISITOS)
  • 1-1  Pessoa     → Aluno        (Pessoa.aluno / Aluno.pessoa)
"""

from datetime import time
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean, CheckConstraint, Column, ForeignKey,
    Integer, Numeric, String, Table, Text, Time, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

# ── Tabela associativa N:N de pré-requisitos ──────────────────────────────────
pre_requisitos_table = Table(
    "pre_requisitos",
    Base.metadata,
    Column(
        "id_curso_principal", Integer,
        ForeignKey("cursos.id_curso", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_curso_pre", Integer,
        ForeignKey("cursos.id_curso", ondelete="CASCADE"),
        primary_key=True,
    ),
    CheckConstraint(
        "id_curso_principal <> id_curso_pre",
        name="ck_curso_diferente",
    ),
)


# ── PESSOAS ───────────────────────────────────────────────────────────────────
class Pessoa(Base):
    __tablename__ = "pessoas"
    __table_args__ = (UniqueConstraint("email", name="un_pessoa_email"),)

    id_pessoa: Mapped[int] = mapped_column(
        "id_pessoa", Integer, primary_key=True, autoincrement=True
    )
    nome:  Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)

    # 1:1 → Aluno
    aluno: Mapped[Optional["Aluno"]] = relationship(
        back_populates="pessoa", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Pessoa id={self.id_pessoa} nome='{self.nome}'>"


# ── ALUNOS ────────────────────────────────────────────────────────────────────
class Aluno(Base):
    __tablename__ = "alunos"
    __table_args__ = (UniqueConstraint("matricula", name="un_aluno_matricula"),)

    id_aluno:  Mapped[int] = mapped_column(
        Integer, ForeignKey("pessoas.id_pessoa", ondelete="CASCADE"), primary_key=True
    )
    matricula: Mapped[str]            = mapped_column(String(20), nullable=False)
    cr:        Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)

    # 1:1 ← Pessoa
    pessoa: Mapped["Pessoa"] = relationship(back_populates="aluno")

    # 1-N → Matricula
    matriculas: Mapped[List["Matricula"]] = relationship(
        back_populates="aluno", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Aluno matricula='{self.matricula}' cr={self.cr}>"


# ── CURSOS ────────────────────────────────────────────────────────────────────
class Curso(Base):
    __tablename__ = "cursos"
    __table_args__ = (
        UniqueConstraint("codigo", name="un_curso_codigo"),
        CheckConstraint("carga_horaria > 0", name="ck_carga_positiva"),
    )

    id_curso:      Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo:        Mapped[str] = mapped_column(String(10),  nullable=False)
    nome:          Mapped[str] = mapped_column(String(100), nullable=False)
    carga_horaria: Mapped[int] = mapped_column(Integer,     nullable=False)
    ementa:        Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # N-N reflexivo: pré-requisitos
    pre_requisitos: Mapped[List["Curso"]] = relationship(
        secondary=pre_requisitos_table,
        primaryjoin=lambda: Curso.id_curso == pre_requisitos_table.c.id_curso_principal,
        secondaryjoin=lambda: Curso.id_curso == pre_requisitos_table.c.id_curso_pre,
        backref="requerido_por",
    )

    # 1-N → Turma
    turmas: Mapped[List["Turma"]] = relationship(
        back_populates="curso", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Curso codigo='{self.codigo}' nome='{self.nome}'>"


# ── TURMAS ────────────────────────────────────────────────────────────────────
class Turma(Base):
    __tablename__ = "turmas"
    __table_args__ = (
        CheckConstraint("vagas_max > 0", name="ck_vagas_positivas"),
    )

    id_turma:  Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_curso:  Mapped[int]  = mapped_column(
        Integer, ForeignKey("cursos.id_curso", ondelete="RESTRICT"), nullable=False
    )
    periodo:   Mapped[str]  = mapped_column(String(10), nullable=False)
    vagas_max: Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)
    status:    Mapped[bool] = mapped_column(Boolean, default=True)

    # N:1 ← Curso
    curso: Mapped["Curso"] = relationship(back_populates="turmas")

    # 1-N → HorarioTurma
    horarios: Mapped[List["HorarioTurma"]] = relationship(
        back_populates="turma", cascade="all, delete-orphan"
    )

    # 1-N → Matricula
    matriculas: Mapped[List["Matricula"]] = relationship(
        back_populates="turma", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Turma id={self.id_turma} periodo='{self.periodo}' curso_id={self.id_curso}>"


# ── HORARIOS_TURMA ────────────────────────────────────────────────────────────
class HorarioTurma(Base):
    __tablename__ = "horarios_turma"
    __table_args__ = (
        CheckConstraint("hora_fim > hora_inicio", name="ck_horario_valido"),
        CheckConstraint(
            "dia_semana IN ('SEG','TER','QUA','QUI','SEX','SAB','DOM')",
            name="ck_dia_semana",
        ),
    )

    id_horario:  Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_turma:    Mapped[int] = mapped_column(
        Integer, ForeignKey("turmas.id_turma", ondelete="CASCADE"), nullable=False
    )
    dia_semana:  Mapped[str]  = mapped_column(String(3), nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fim:    Mapped[time] = mapped_column(Time, nullable=False)

    # N:1 ← Turma
    turma: Mapped["Turma"] = relationship(back_populates="horarios")

    def __repr__(self) -> str:
        return (
            f"<HorarioTurma turma={self.id_turma} "
            f"{self.dia_semana} {self.hora_inicio}-{self.hora_fim}>"
        )


# ── MATRICULAS ────────────────────────────────────────────────────────────────
class Matricula(Base):
    __tablename__ = "matriculas"
    __table_args__ = (
        UniqueConstraint("id_aluno", "id_turma", name="un_aluno_turma"),
        CheckConstraint(
            "nota_final IS NULL OR (nota_final >= 0 AND nota_final <= 10)",
            name="ck_nota_valida",
        ),
        CheckConstraint(
            "frequencia IS NULL OR (frequencia >= 0 AND frequencia <= 100)",
            name="ck_frequencia_valida",
        ),
        CheckConstraint(
            "situacao IN ('CURSANDO','APROVADO','REPROVADO','TRANCADO')",
            name="ck_situacao_valida",
        ),
    )

    id_matricula: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_aluno:     Mapped[int] = mapped_column(
        Integer, ForeignKey("alunos.id_aluno", ondelete="RESTRICT"), nullable=False
    )
    id_turma:     Mapped[int] = mapped_column(
        Integer, ForeignKey("turmas.id_turma", ondelete="RESTRICT"), nullable=False
    )
    nota_final:  Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    frequencia:  Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    situacao:    Mapped[Optional[str]]     = mapped_column(String(20),    nullable=True)

    # N:1 ← Aluno
    aluno: Mapped["Aluno"] = relationship(back_populates="matriculas")

    # N:1 ← Turma
    turma: Mapped["Turma"] = relationship(back_populates="matriculas")

    def __repr__(self) -> str:
        return (
            f"<Matricula aluno={self.id_aluno} turma={self.id_turma} "
            f"situacao='{self.situacao}'>"
        )
