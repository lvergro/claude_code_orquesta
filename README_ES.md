# <img src="assets/logo.png" alt="Orquesta Logo" width="50" height="50" align="center"/> Orquesta

> **Nota:** Esta es una forma de orquestación que he estado probando en algunos proyectos. Toma lo que te sirva, cambia lo que no.

**Orquesta** es un framework de orquestación multi-agente que convierte a Claude Code en un equipo de desarrollo con roles especializados, memoria persistente y flujos automatizados.

Usa **dispatch nativo** — los agents tienen `description` en su frontmatter YAML y Claude los invoca automáticamente. Las skills usan el formato estándar `name/SKILL.md` con `user-invocable: true`.

**[Read in English](README.md)**

## 🤝 Herramientas Recomendadas

Recomendamos usar **[Claude Code Templates](https://github.com/davila7/claude-code-templates)** creado por **davila7** junto con Orquesta.
Específicamente, el **Analytics Dashboard** (`npx claude-code-templates --analytics`) ofrece una visualización en tiempo real del proceso de pensamiento de tus agentes de Orquesta y el uso de tokens.

---

Este framework provee una convención basada en archivos que le da estas capacidades a Claude Code sin herramientas externas. Son solo archivos markdown y YAML — Claude los lee y sigue las instrucciones.

---

## Dos Variantes

El framework viene en dos variantes. Elige la que se ajuste a tu flujo de trabajo:

| | **Linear** (`.claude/`) | **Feature-driven** (`worktree/.claude/`) |
|---|---|---|
| **Flujo** | Un cambio a la vez, secuencial | Un issue = un worktree = un branch |
| **GitHub Issues** | No | Si — lee/crea issues, comenta progreso, crea PRs |
| **Aislamiento** | Trabaja en el directorio actual | Un worktree por feature, trabajo en paralelo |
| **Trazabilidad** | Commits convencionales | Issue → spec → worktree → commits → PR |
| **Resumibilidad** | `/develop` retoma desde `project-state.md` | `/feature #42` retoma desde el worktree |
| **Ideal para** | Trabajo solo, proyectos simples | Equipos, proyectos con issues, multiples features |

Puedes empezar con Linear y cambiar a Feature-driven despues — la variante Feature-driven es un superset (mismos agents + skills + una skill extra).

---

## Guia de Implementacion

### Paso 1: Copiar el framework

**Variante Linear** — trabajo secuencial, sin GitHub Issues:

```bash
# Desde la raiz de tu proyecto
cp -r /ruta/al/framework/.claude/ ./.claude/
```

**Variante Feature-driven** — con GitHub Issues, worktrees y PRs:

```bash
# Desde la raiz de tu proyecto
cp -r /ruta/al/framework/worktree/.claude/ ./.claude/
```

> Ambas variantes incluyen los mismos agents, skills y memoria. La variante feature-driven agrega la skill `/feature` y permisos para `gh` y `git worktree`.

### Paso 2: Configurar tu proyecto

Edita `.claude/project.yml` — define QUE es tu proyecto:

```yaml
name: MiSaaS
description: Plataforma de gestion de inventarios

domain:
  language: es
  entities:
    - organization (tenant)
    - user
    - warehouse
    - product
    - order

tenant:
  enabled: true
  column: org_id
  table: organizations
  isolation: rls

invariants:
  - name: Tenant Isolation
    rule: All DB queries filter by org_id. No cross-tenant data leaks.
    severity: critical
  - name: Stock Integrity
    rule: Stock decrements MUST be atomic. No overselling.
    severity: critical

critical_flows:
  - name: Order Fulfillment
    description: Validate stock → reserve → charge → dispatch
    tables: [orders, inventory, payments]
    type: transaction

gate_protected_areas:
  - pattern: "migrations/"
    reason: Schema changes require /develop
  - pattern: "middleware*"
    reason: Auth and routing
```

### Paso 3: Configurar tu stack

Edita `.claude/stack.yml` — define COMO se ejecuta:

```yaml
name: node-docker-prisma

runtime:
  exec_prefix: "docker compose exec api"
  note: "No local runtime. Always use exec_prefix."

commands:
  install: "npm install"
  test: "npx vitest run"
  test_single: "npx vitest run {file}"
  lint: "npx eslint {path}"
  type_check: "npx tsc --noEmit"
  build: "npm run build"
  dev: "npm run dev"
  validate: "npx vitest run && npm run build"  # tests + build (detecta errores de runtime)

paths:
  source: "src/"
  tests: "tests/"
  migrations: "prisma/migrations/"
  config: "package.json"

conventions:
  test_file_pattern: "{name}.test.ts"
  module_structure: "src/{module}/"

framework:
  name: "Express + Prisma"
  backend: "PostgreSQL"
  orm: "Prisma"
```

Otros ejemplos de stack:

```yaml
# Python + FastAPI
name: python-docker
runtime:
  exec_prefix: "docker compose exec api"
commands:
  test: "pytest"
  lint: "ruff check {path}"
  type_check: "mypy {path}"
paths:
  source: "app/"
  tests: "tests/"
conventions:
  test_file_pattern: "test_{name}.py"

# Go (sin Docker)
name: go-local
runtime:
  exec_prefix: ""
commands:
  test: "go test ./..."
  lint: "golangci-lint run"
paths:
  source: "internal/"
  tests: "internal/"
conventions:
  test_file_pattern: "{name}_test.go"
```

### Paso 4: Documentar tu arquitectura

Edita `.claude/memory/architecture.md` — la fuente de verdad del diseno de tu sistema:

- Overview del sistema
- Stack y modelo de ejecucion
- Modelo de datos (entidades, relaciones)
- Roles y autorizacion
- Flujos criticos (contratos: inputs → validaciones → pasos → outputs)
- Patrones prohibidos

Los agents consultan este archivo antes de escribir cualquier codigo.

### Paso 5: Empezar a usar

```bash
claude
# Dentro de Claude Code:
/develop Implementar sistema de notificaciones
/quick Cambiar el texto del boton de login
/research Comparar Redis vs Memcached para caching
/feature #42                              # (Solo feature-driven)
/feature Agregar sistema de alertas       # (Solo feature-driven)
```

---

## Como Funciona

### Estructura

```
tu-proyecto/
├── .claude/
│   ├── CLAUDE.md                          # Entry point — refs a project.yml, stack.yml, models.yml
│   ├── project.yml                        # QUE: identidad, dominio, invariantes, flujos criticos
│   ├── stack.yml                          # COMO: runtime, comandos, paths, convenciones
│   ├── models.yml                         # Routing de modelos: complejidad → haiku/sonnet/opus
│   ├── settings.local.json                # Permisos de herramientas
│   │
│   ├── agents/                            # 3 subagents con frontmatter nativo
│   │   ├── planner.md                     #   Planifica, disena, investiga
│   │   ├── builder.md                     #   Codifica, testea, ejecuta
│   │   └── git.md                         #   Commit, push (safety gate)
│   │
│   ├── skills/                            # Flujos invocables (/nombre)
│   │   ├── develop/SKILL.md               #   Pipeline E2E completo
│   │   ├── quick/SKILL.md                 #   Fast-path sin planificacion
│   │   ├── research/SKILL.md              #   Investigacion tecnica
│   │   ├── feature/SKILL.md               #   (Feature-driven) Pipeline Issue → PR
│   │   ├── parallel/SKILL.md              #   Ejecucion multi-sesion
│   │   ├── audit/SKILL.md                 #   Auditoria de seguridad
│   │   ├── summarize-context/SKILL.md     #   Compresion de contexto
│   │   ├── validate-invariants/SKILL.md   #   Verificacion de invariantes
│   │   ├── write-tests/SKILL.md           #   Estrategia de testing
│   │   ├── prepare-commit/SKILL.md        #   Generar commit message
│   │   ├── analyze-architecture/SKILL.md  #   Detectar drift arquitectonico
│   │   └── archive-state/SKILL.md         #   Archivar estado completado
│   │
│   └── memory/                            # Estado persistente
│       ├── architecture.md                #   Diseno del sistema (source of truth)
│       ├── project-state.md               #   Tareas en curso (cap 80 lineas)
│       ├── research.md                    #   Log de investigaciones
│       ├── locks.md                       #   Coordinacion multi-sesion (TTL 30 min)
│       ├── decisions/                     #   Registro de decisiones arquitectonicas
│       │   └── TEMPLATE.md                #     Plantilla DEC-####.md
│       └── archive/                       #   Estados completados
```

### Agents

Los agents tienen `description` y `allowed-tools` en su frontmatter YAML. Claude Code los invoca automaticamente cuando la tarea encaja.

| Agent | Rol | Puede | No puede |
|-------|-----|-------|----------|
| `planner` | Planificador + Arquitecto + Investigador | Leer, analizar, disenar, escribir en memory/ | Codigo, commits, Bash |
| `builder` | Programador + QA | Escribir codigo, tests, ejecutar comandos | Editar arquitectura, commits |
| `git` | Release Manager | Commits y push | Escribir codigo o editar archivos |

### Skills

Las skills son flujos que se invocan con `/nombre` dentro de Claude Code.

**Principales:**

| Skill | Cuando usarla | Variante |
|-------|---------------|----------|
| `/develop` | Feature nueva, bug complejo, cualquier cambio que necesite planificacion | Ambas |
| `/quick` | Cambio trivial que no toca areas protegidas (typo, CSS, campo simple) | Ambas |
| `/research` | Evaluar opciones tecnicas antes de decidir | Ambas |
| `/feature` | Pipeline E2E: issue → spec → worktree → implementacion → PR | Feature-driven |

**Auxiliares:**

| Skill | Que hace |
|-------|----------|
| `/parallel` | Ejecuta tareas de la wave actual en multiples terminales |
| `/audit` | Auditoria de seguridad del codebase |
| `/write-tests` | Define estrategia de testing y genera tests |
| `/prepare-commit` | Valida tests + genera mensaje de commit convencional |
| `/validate-invariants` | Verifica que no se rompan reglas criticas |
| `/analyze-architecture` | Compara el codigo actual vs architecture.md |
| `/summarize-context` | Comprime el estado para liberar tokens |
| `/archive-state` | Archiva estado completado y resetea el tracker |

---

## Flujos de Trabajo

### `/develop` — Pipeline completo

El flujo principal. Planifica, implementa en loop, y commitea.

```
PHASE 0: Triage
  Lee project-state.md → hay tareas pendientes? → RESUME
  Analiza request → necesita cambio de arquitectura?

PHASE 1: Architecture (condicional)
  Lee decisions/ para no re-litigar decisiones pasadas
  Planner agent actualiza architecture.md
  Registra nuevas decisiones como DEC-####.md

PHASE 2: Execution Loop
  Por cada tarea [ ] en project-state.md:
    Builder agent implementa + testea
    PASS → marca [x], persiste estado
    FAIL → reintenta (max 2) → STOP si falla 3x
  Cada 3 tareas → /summarize-context

PHASE 3: Finalization
  Ejecutar validate (tests + build) → detecta errores de runtime
  Git agent commit + push
  /archive-state → resetea project-state.md
```

### `/quick` — Fast path

Para cambios triviales que no requieren planificacion.

```
Gate: Lee project.yml → toca area protegida?
  SI → ABORT, sugiere /develop

Preflight:
  git diff --stat → >5 archivos o >200 lineas? → ABORT, sugiere /develop
  /validate-invariants → FAIL? → ABORT

Build:
  Builder agent implementa → Git agent commitea
```

### `/feature` — Issue-to-PR (variante feature-driven)

Pipeline completo desde GitHub Issue hasta Pull Request, con aislamiento por worktree.

```
PHASE 0: Resume Check
  Parse input (#42, URL, o descripcion libre)
  gh auth status → verificar autenticacion
  Si worktree existe → RESUME desde fase pendiente

PHASE 1: Intake
  Descripcion libre → gh issue create
  Issue existente → leer contenido
  Auto-label: enhancement, bug, o documentation

PHASE 2: Spec
  Planner agent (opus) produce spec estructurada + criterios de aceptacion
  Aplicar labels del analisis
  Post Comment 1 — Requirements (inmutable)
  Post Comment 2 — Execution Plan (vivo, se actualiza durante ejecucion)
  Escribir tasks a project-state.md

PHASE 3: Worktree Setup
  git fetch origin
  git worktree add WT_ROOT -b feat/ISSUE-SLUG origin/main
  Copiar state al worktree

PHASE 4: Execution (dentro del worktree — aislamiento estricto)
  NUNCA leer/escribir en REPO_ROOT — el worktree es la raiz del proyecto
  Builder agent (sonnet) implementa + testea cada task
  Commits por wave dentro del worktree
  Actualizar Comment 2 con progreso despues de cada wave

PHASE 5: Integration
  Ejecutar validate (tests + build) → detecta errores de runtime
  git push → gh pr create (haiku)
  Actualizacion final de Comment 2 con PR URL

PHASE 6: Cleanup
  Archivar state (haiku)
  NO remover worktree (puede necesitar fixes post-review)
```

**Ejemplo de uso:**

```bash
claude
# Dentro de Claude Code:
/feature #42                          # Implementar issue existente
/feature Agregar sistema de alertas   # Crear issue + implementar
/feature #42                          # Resumir si fue interrumpido
```

**Convencion de paths:**

```
mi-proyecto/                         # REPO_ROOT (checkout principal)
├── .claude/
├── src/
└── ...

.worktrees/                          # Directorio hermano al repo
├── feat/42-add-notifications/       # Worktree para issue #42
└── feat/57-fix-auth/                # Otra feature en paralelo
```

### `/parallel` — Multi-sesion

Abre multiples terminales de Claude Code para ejecutar tareas de la misma wave en paralelo:

```bash
# Terminal 1        # Terminal 2        # Terminal 3
/parallel           /parallel           /parallel
```

Cada sesion toma una tarea diferente via coordinacion en `locks.md`. Locks con mas de 30 minutos se consideran expirados y se liberan automaticamente.

---

## Que Editar por Proyecto

Solo 4 archivos contienen datos de tu proyecto. El resto es framework generico.

| Archivo | Que poner | Cuando editarlo |
|---------|-----------|-----------------|
| `project.yml` | Nombre, dominio, tenant config, invariantes, flujos criticos, areas protegidas | Al adoptar el framework |
| `stack.yml` | Runtime, comandos, paths, convenciones del stack | Al adoptar el framework |
| `models.yml` | Routing de modelos: que modelo Claude (haiku/sonnet/opus) por tipo de tarea | Al adoptar el framework o ajustar costos |
| `memory/architecture.md` | Diseno del sistema, modelo de datos, roles, patrones | Al inicio y cuando evolucione la arquitectura |

Agents, skills y CLAUDE.md **no se editan** — son genericos y referencian `{stack.*}` y `{project.*}`.

---

## Memoria y Resiliencia

### Archivos de memoria

| Archivo | Funcion | Quien escribe |
|---------|---------|---------------|
| `architecture.md` | Diseno del sistema | Planner agent |
| `project-state.md` | Tareas activas, progreso, foco | Planner + skills |
| `research.md` | Investigaciones tecnicas | Planner agent |
| `decisions/DEC-*.md` | Decisiones arquitectonicas con contexto y alternativas | Planner agent |
| `locks.md` | Coordinacion entre sesiones (TTL 30 min) | /parallel |

### Mecanismos de resiliencia

- **Persistencia atomica**: El estado se escribe en `project-state.md` despues de cada tarea. Si la sesion se interrumpe, `/develop` o `/feature` retoman automaticamente.
- **Compresion de contexto**: `/summarize-context` se ejecuta cada 3 tareas, manteniendo el tracker bajo 80 lineas.
- **Archivado**: `/archive-state` mueve estados completados a `memory/archive/` y resetea el tracker.
- **Decision log**: Las decisiones arquitectonicas se persisten en `memory/decisions/` para evitar re-litigar en sesiones futuras.
- **Lock TTL**: Los locks en `/parallel` expiran despues de 30 minutos, evitando bloqueos huerfanos por sesiones interrumpidas.

---

## Extender el Framework

Esto es un punto de partida. Modificalo libremente.

### Agregar un agent

Crea `.claude/agents/mi-agent.md`:

```yaml
---
description: >
  Descripcion de cuando Claude debe invocar este agent.
  Incluye el contexto de uso para que el dispatch automatico funcione.
allowed-tools:
  - Read
  - Grep
  - Bash
disallowed-tools:
  - Write
---

# Mi Agent

Instrucciones del rol.
```

### Agregar una skill

Crea `.claude/skills/mi-skill/SKILL.md`:

```yaml
---
name: mi-skill
description: >
  Que hace esta skill y cuando invocarla.
user-invocable: true
---

# /mi-skill

## Flow
1. Paso uno
2. Paso dos
```

### Conectar un MCP de base de datos

Si tu proyecto usa una base de datos, puedes configurar un servidor [Model Context Protocol](https://modelcontextprotocol.io/) para que el planner agent inspeccione el schema real en vez de depender de documentacion que puede estar desactualizada.

En `stack.yml`:

```yaml
database:
  type: "postgresql"              # postgresql, mysql, sqlite, mongodb
  schema_source: "schema.sql"     # Archivo fallback si no hay MCP
  mcp: true                       # true si hay un MCP de DB configurado
  read_only: true                 # El MCP NUNCA debe escribir en la base de datos
```

Cuando `database.mcp: true`, el planner usa herramientas MCP para consultar el schema en vivo. Cuando es `false` o no existe, lee el archivo `schema_source` como fallback.

### Agregar permisos de herramientas

Edita `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(docker compose exec:*)",
      "Bash(tree:*)",
      "Bash(test:*)"
    ]
  }
}
```

---

## FAQ

**Funciona sin Docker?**
Si. En `stack.yml` pon `exec_prefix: ""` y los comandos se ejecutan directamente.

**Puedo usarlo con otro LLM?**
Esta disenado para Claude Code, pero los archivos `.md` son instrucciones en lenguaje natural que otros LLMs pueden interpretar.

**Que pasa si Claude ignora una restriccion?**
Las restricciones estan en 3 niveles: `project.yml` (invariantes), `architecture.md` (patrones), y `project-state.md` (contexto activo). `/summarize-context` refresca el estado periodicamente.

**Puedo usar solo algunas skills?**
Si. Cada skill es independiente. Puedes borrar las que no necesites.

**Necesito ambas variantes?**
No. Elige una. Si trabajas solo en un proyecto simple, Linear esta bien. Si trabajas con GitHub Issues y quieres aislamiento por worktree, usa Feature-driven.

**Es esta la forma "correcta" de usar Claude Code?**
No. Es un enfoque que funciona bien para desarrollo estructurado y multi-paso. Claude Code es flexible — puede que encuentres una organizacion completamente diferente que te funcione mejor. Usa esto como inspiracion, no como dogma.

---

## Licencia

Estructura de uso libre. Adaptala a tu proyecto.
