# Sistema de Gestão Acadêmica — ORM com SQLAlchemy

**UFCA — Universidade Federal do Cariri**  
Disciplina: `ADS0011 — Projeto de Banco de Dados`  
Semestre: `2025.2`  
Nome: Eduardo Magalhães · Matrícula: `2025013209`

---

## 📌 Sobre o projeto

Aplicação Python que conecta ao banco PostgreSQL criado nas etapas anteriores
e realiza mapeamento ORM completo com **SQLAlchemy 2.x**, cobrindo:

| Parte | O que foi feito |
|-------|-----------------|
| 1 | Configuração da conexão via `.env` |
| 2 | Mapeamento ORM de todas as 6 tabelas + relacionamentos |
| 3 | CRUD completo via ORM (CREATE / READ / UPDATE / DELETE) |
| 4 | 3 consultas com relacionamento (JOIN, N:N, filtro+ordem) + bônus aggregation |

---

## 🗂 Estrutura do projeto

```
projeto_orm/
├── main.py                  # Ponto de entrada — executa tudo em sequência
├── database.py              # Engine, SessionLocal e Base declarativa
├── .env.example             # Modelo de variáveis de ambiente
├── requirements.txt         # Dependências Python
├── models/
│   └── __init__.py          # Entidades ORM (Pessoa, Aluno, Curso, Turma …)
├── operations/
│   └── crud.py              # CREATE / READ / UPDATE / DELETE via ORM
└── queries/
    └── consultas.py         # Consultas com JOIN, N:N, filtro + ordenação
```

---

## ⚙️ Pré-requisitos

- Python 3.11+
- PostgreSQL 14+ rodando localmente (ou acessível via rede)
- O banco **já deve existir e estar populado** com o script DDL+DML das etapas anteriores

---

## 🚀 Como executar

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd projeto_orm
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

Copie `.env.example` para `.env` e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
DB_NAME=gestao_academica
```

> O banco `gestao_academica` precisa existir e ter as tabelas criadas.  
> Execute o script `banco.sql` (DDL + DML) antes de rodar a aplicação, se ainda não tiver feito.

### 5. Execute

```bash
python main.py
```

---

## 🗄️ Script do banco

O arquivo `banco.sql` na raiz do repositório contém o DDL completo
(criação de tabelas, constraints, índices) e o DML com dados de teste.

Para recriar o banco do zero:

```bash
psql -U postgres -d gestao_academica -f banco.sql
```

---

## 📋 Mapeamento ORM

| Tabela SQL       | Classe Python  | Relacionamentos mapeados |
|------------------|----------------|--------------------------|
| `PESSOAS`        | `Pessoa`       | 1:1 → `Aluno` |
| `ALUNOS`         | `Aluno`        | 1:1 ← `Pessoa` · 1-N → `Matricula` |
| `CURSOS`         | `Curso`        | N:N reflexivo `pre_requisitos` · 1-N → `Turma` |
| `PRE_REQUISITOS` | *(tabela assoc.)* | via `secondary` em `Curso.pre_requisitos` |
| `TURMAS`         | `Turma`        | N:1 ← `Curso` · 1-N → `HorarioTurma` · 1-N → `Matricula` |
| `HORARIOS_TURMA` | `HorarioTurma` | N:1 ← `Turma` |
| `MATRICULAS`     | `Matricula`    | N:1 ← `Aluno` · N:1 ← `Turma` |

---

## 🔄 Operações CRUD

| Operação | Função | Descrição |
|----------|--------|-----------|
| **CREATE** | `inserir_novos_alunos()` | Insere 3 Pessoas + Alunos |
| **READ**   | `listar_alunos()` | Lista com paginação e ordenação dinâmica |
| **UPDATE** | `atualizar_cr_aluno()` | Atualiza o CR de um aluno pela matrícula |
| **DELETE** | `remover_aluno()` | Remove Aluno + Pessoa (CASCADE) |

---

## 🔍 Consultas com relacionamento

| # | Função | Tipo |
|---|--------|------|
| 1 | `listar_matriculas_ativas()` | JOIN 1-N/N-1 (Aluno→Turma→Curso) |
| 2 | `cursos_e_pre_requisitos()` | JOIN N:N reflexivo |
| 3 | `top_alunos_por_cr()` | Filtro (`cr IS NOT NULL`) + ordenação (`cr DESC`) |
| + | `aprovados_por_disciplina()` | Agregação `COUNT / AVG` com GROUP BY (bônus) |

---

## 📸 Exemplo de saída

```
======================================================================
  SISTEMA DE GESTÃO ACADÊMICA — ORM com SQLAlchemy
======================================================================
  Conexão OK  ✔  PostgreSQL 16.x on x86_64-pc-linux-gnu

──────────────────────────────────────────────────────────────────────
  PARTE 3 — CRUD VIA ORM
──────────────────────────────────────────────────────────────────────

[CREATE] 3 alunos inseridos com sucesso.
  ↳ Hugo Cavalcante Barros      |  matrícula: 2025013210
  ↳ Isabela Freitas Nunes       |  matrícula: 2025013211
  ↳ João Victor Melo            |  matrícula: 2025013212

[READ] Página 1 | 5 por página | total de alunos: 10
  [2023014501] Ana Carolina Silva Santos          CR: 8.75
  [2023014502] Bruno Henrique Oliveira Costa      CR: 7.50
  ...

[UPDATE] CR de 'Hugo Cavalcante Barros' atualizado: None → 7.85

[DELETE] Aluno 'João Victor Melo' (matrícula: 2025013212) removido com sucesso.

──────────────────────────────────────────────────────────────────────
  PARTE 4 — CONSULTAS COM RELACIONAMENTO
──────────────────────────────────────────────────────────────────────

[CONSULTA 1 — JOIN] Matrículas ativas (CURSANDO):
  Aluno                               Matrícula       Disciplina                          Período    Freq.
  ─────────────────────────────────────────────────────────────────────────────────────────────────────────
  Ana Carolina Silva Santos           2023014501      Desenvolvimento Web                 2025.2     100.0%
  ...

[CONSULTA 2 — JOIN N:N] Cursos e pré-requisitos:
  Código       Disciplina                               Pré-requisitos
  ─────────────────────────────────────────────────────────────────────────────────────
  ADS0001      Introdução à Programação                 Nenhum
  ADS0002      Programação Orientada a Objetos          ADS0001
  ...

[CONSULTA 3 — FILTRO + ORDEM] Top 5 alunos por CR:
  Pos.   Nome                                Matrícula       CR
  ─────────────────────────────────────────────────────────────────
  1      Camila Rodrigues Ferreira           2024010101      9.20
  2      Ana Carolina Silva Santos           2023014501      8.75
  ...
```
