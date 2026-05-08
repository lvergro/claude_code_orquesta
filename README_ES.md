# <img src="assets/logo.png" alt="Orquesta Logo" width="50" height="50" align="center"/> Orquesta

**Sistema de orquestación de desarrollo para Claude Code.**

Sistema basado en archivos que estructura cómo Claude Code **diseña, planifica, implementa y entrega** features — con roles de subagentes, memoria persistente y workflows orientados a issues.

**Una feature = un issue = un worktree = una rama = un PR.**

**[Read in English](README.md)**

---

## Cómo funciona

Cuatro subagentes con acceso a herramientas **enforced** (mediante `tools` / `disallowedTools` en frontmatter), despachados automáticamente:

| Agent | Rol | Modelo | Puede | No puede |
|-------|-----|--------|-------|----------|
| `planner` | Arquitecto + Investigador | `opus` | Leer, analizar, diseñar, escribir en memory/ y docs/ | Bash, código, commits |
| `builder` | Programador | `sonnet` | Escribir código, tests, ejecutar comandos | Push, editar áreas gate-protected |
| `git` | Release Manager | `haiku` | Commits y push | Edit/Write de cualquier archivo |
| `qa` | Validador QA | `sonnet` | Tests, automatización de browser, reportes | (sin restricción de edición de fuente aún — por convención) |

---

## Workflow en dos etapas: diseñar y luego construir

Orquesta cubre el camino completo desde *idea* hasta *feature entregada* en dos etapas:

```
                        ┌──────────────────────┐         ┌──────────────────────┐
   idea / brief  ─────► │ pipeline /discovery  │ ──────► │  pipeline /feature   │ ─────► PR
                        │ (artefactos diseño)  │         │  (issue → código)    │
                        └──────────────────────┘         └──────────────────────┘
                          docs/  +  .claude/                código  +  tests
```

### Etapa 1 — `/discovery` (diseño)

Pipeline conversacional dirigido por el `planner` que produce artefactos de diseño en `docs/` y siembra `.claude/` con ellos. Se ejecuta una vez al inicio del proyecto, y luego se vuelven a correr fases individuales cuando el diseño evoluciona.

| # | Fase | Output |
|---|------|--------|
| 1 | `/discovery-vision` | `docs/glossary.md` + resumen de visión |
| 2 | `/discovery-functional` | `docs/requirements/functional.md` |
| 3 | `/discovery-use-cases` | `docs/use-cases/UC-*.md` |
| 4 | `/discovery-nfr` | `docs/requirements/non-functional.md` |
| 5 | `/discovery-architecture` | `docs/architecture/c4-*.md` (Context, Container, Component) |
| 6 | `/discovery-decisions` | `docs/decisions/ADR-*.md` |
| 7 | `/discovery-intake` | deriva artefactos compactos de runtime (`.claude/project.yml`, resumen `memory/architecture.md`, índice `memory/requirements.md`) desde `docs/`. Los ADRs quedan en `docs/decisions/`. |

Cada fase autodetecta el modo según el estado de `docs/`:

- **greenfield** — sin docs todavía → Q&A conversacional crea la primera versión.
- **review** — docs existen pero con issues → auditoría (completitud / consistencia interna / drift con el código) → iterar.
- **ingest** — docs completos y frescos → confirmar y avanzar.

El recorrido detallado (con sesiones de ejemplo para cada escenario) está en [Recorrido de discovery](#recorrido-de-discovery) más abajo.

#### Modelo híbrido: diseño en `docs/`, estado en tu tracker

Cuando un proyecto configura `stack.yml → tracker.type: linear` (u otro tracker soportado), `/discovery-intake` espeja cada FR aprobado como **issue padre** en el tracker. Luego `/feature FR-01` crea un sub-issue hijo bajo ese padre, lo enlaza al worktree, y los PRs lo cierran al mergear.

| Capa | Vive en | Dueño |
|------|---------|-------|
| Diseño del FR (qué, actor, criterios) | `docs/requirements/functional.md` | `/discovery-functional` (aprobación humana) |
| Estado del FR (pendiente / en curso / shipped) | Linear (u otro tracker) — issue padre por FR | `/discovery-intake` sincroniza; PRs cierran hijos |
| Implementación (la feature concreta) | Issue hijo del tracker + worktree + PR | `/feature FR-N` |

Si no configuras un tracker, `/discovery-intake` salta el sync silenciosamente y `/feature` igual funciona con texto libre o issues de GitHub.

### Etapa 2 — `/feature` (construcción)

Una vez sembrado `.claude/`, cada feature sigue un único pipeline:

```
/feature #42  (o descripción en texto libre)

PHASE 0 → Sync de schema + verificación de resume
PHASE 1 → Intake (crear/leer issue de GitHub, auto-label)
PHASE 2 → Spec (planner: alcance, criterios de aceptación, tareas en waves)
PHASE 3 → Setup de worktree (rama + directorio aislado)
PHASE 4 → Ejecución (builder: implementar + testear cada tarea, commit por wave)
PHASE 5 → Integración (validar, push, crear PR)
PHASE 6 → Cleanup (archivar estado)
```

¿Se interrumpió? Ejecutar `/feature #42` de nuevo — retoma desde donde quedó.

¿Features en paralelo? Múltiples terminales, cada una con un `/feature #N` distinto. Cada worktree está completamente aislado.

---

## Estructura

```
.claude/
├── CLAUDE.md                           # Entry point — importa project.yml + stack.yml
├── project.yml                         # QUÉ: dominio, invariantes, áreas gate-protected
├── stack.yml                           # CÓMO: runtime, comandos, paths, fuente de schema
│
├── settings.json                       # Compartido: permisos (deny/ask), hooks
├── settings.local.json                 # Personal/local: allows extra (gitignoreable)
│
├── hooks/                              # Hooks de ciclo de vida (corren como shell scripts)
│   ├── gate-check.sh                   #   PreToolUse Edit|Write — bloquea gate_protected_areas
│   └── session-context.sh              #   SessionStart — inyecta Current Focus de project-state
│
├── rules/                              # Reglas con paths (cargan solo al tocar archivos matching)
│   ├── migrations.md                   #   paths: migrations/**, prisma/schema.prisma
│   └── tests.md                        #   paths: **/*.test.*, tests/**
│
├── agents/                             # Subagentes — model + tools enforced via frontmatter
│   ├── planner.md                      #   model: opus  — diseña, nunca codea
│   ├── builder.md                      #   model: sonnet — codea silencioso
│   ├── git.md                          #   model: haiku — commits + push
│   └── qa.md                           #   model: sonnet — tests + browser E2E
│
├── skills/                             # Workflows (slash commands)
│   │  # ── Discovery (etapa 1 — diseño) ──
│   ├── discovery/SKILL.md              #   /discovery — orquestador (detección de modo + estado)
│   ├── discovery-vision/SKILL.md       #     fase 1: glossary + visión
│   ├── discovery-functional/SKILL.md   #     fase 2: requisitos funcionales
│   ├── discovery-use-cases/SKILL.md    #     fase 3: casos de uso
│   ├── discovery-nfr/SKILL.md          #     fase 4: requisitos no-funcionales
│   ├── discovery-architecture/SKILL.md #     fase 5: arquitectura C4
│   ├── discovery-decisions/SKILL.md    #     fase 6: ADRs
│   ├── discovery-intake/SKILL.md       #     fase 7: docs/ → .claude/
│   │  # ── Build (etapa 2) ──
│   ├── feature/SKILL.md                #   /feature — pipeline principal de construcción
│   ├── qa-test/SKILL.md                #   /qa-test — validación QA E2E
│   ├── research/SKILL.md               #   /research — investigación técnica
│   ├── audit/SKILL.md                  #   /audit — auditoría de seguridad
│   ├── sync-schema/SKILL.md            #   /sync-schema — sync del modelo de datos
│   ├── prepare-commit/SKILL.md         #   /prepare-commit
│   ├── validate-invariants/SKILL.md    #   Chequeos de seguridad
│   ├── summarize-context/SKILL.md      #   Compresión de contexto
│   ├── write-tests/SKILL.md            #   Estrategia de tests
│   ├── analyze-architecture/SKILL.md   #   Detección de drift
│   └── archive-state/SKILL.md          #   Ciclo de vida del estado
│
└── memory/                             # Estado runtime compacto — derivado de docs/, sin duplicar
    ├── architecture.md                 #   Resumen ejecutivo, ~30 líneas (C4 completo en docs/architecture/)
    ├── requirements.md                 #   Índice FR↔UC (una línea por FR)
    ├── schema.md                       #   Modelo de datos (auto-sync desde stack.yml)
    ├── project-state.md                #   Tareas activas + Current Focus + Blockers
    ├── research.md                     #   Log de investigación
    └── archive/                        #   Estados completados
                                        #   (sin decisions/ — los ADRs se leen directo desde docs/decisions/)
```

El pipeline `/discovery` también crea un árbol `docs/` en la raíz del repositorio:

```
docs/
├── glossary.md                         # Entidades del dominio + resumen de visión
├── requirements/
│   ├── functional.md                   # Lista de FRs
│   └── non-functional.md               # Lista de NFRs (cada NFR debe ser medible)
├── use-cases/                          # UC-NN-*.md (uno por caso de uso)
├── architecture/                       # c4-context.md, c4-container.md, c4-component.md
├── decisions/                          # ADR-NNN-*.md
└── .discovery-state.md                 # Estado por fase, modo, e issues abiertos
```

---

## Inicio rápido

Dos caminos: **A. Proyecto nuevo** (greenfield) o **B. Proyecto existente** (brownfield). Ambos toman `/discovery` como primer comando recomendado — es lo que construye (o audita) los artefactos de diseño que `.claude/` consume.

### A. Proyecto nuevo desde cero

Para un proyecto que no existe todavía, o uno sin código en producción.

```bash
# 1. Crear el proyecto + repo git
mkdir mi-saas && cd mi-saas
git init

# 2. Copiar el framework
cp -r /ruta/a/claude-code-orquesta/.claude ./.claude

# 3. (Opcional) ignorar settings local
echo ".claude/settings.local.json" >> .gitignore

# 4. Abrir Claude Code
claude
```

Luego, en Claude Code:

```
> /discovery
```

`/discovery` recorre 7 fases (visión → requisitos → casos de uso → NFRs → C4 → ADRs → intake), un turno conversacional a la vez. La fase final siembra `.claude/project.yml` y `memory/architecture.md` para que `/feature` tenga una fuente de verdad real desde la cual trabajar.

Cuando el intake termina, el planner sugiere la primera feature — típicamente el scaffold del proyecto:

```bash
/feature Bootstrap del proyecto — scaffold Next.js + Supabase + Prisma
```

El `planner` produce el spec, el `builder` ejecuta tarea por tarea, y el `git` hace commit por wave.

Ver [Recorrido de discovery → Escenario 1](#escenario-1--proyecto-completamente-nuevo) para un ejemplo paso a paso.

---

### B. Proyecto existente (brownfield)

Para un proyecto que ya tiene código, tests e historia en producción. El objetivo es enseñarle al framework lo que ya existe, no regenerarlo.

```bash
# 1. Desde la raíz del proyecto
cp -r /ruta/a/claude-code-orquesta/.claude ./.claude

# 2. Agregar settings local al .gitignore (opcional)
echo ".claude/settings.local.json" >> .gitignore

# 3. Abrir Claude Code en el repo
claude
```

Dos sub-caminos según qué documentación de diseño exista:

**B.1 — Ya hay docs de diseño** (en Notion, Confluence, markdown). Copiar a `docs/` siguiendo la convención de [Estructura](#estructura) y luego ejecutar:

```
> /discovery review --deep
```

El planner audita cada artefacto (completitud, consistencia interna, drift con el código real) y recorre los issues uno por uno. Cuando todo está limpio, `/discovery-intake` siembra `.claude/`.

**B.2 — No hay docs de diseño todavía.** Ejecutar `/discovery` y responder según lo que el código actual hace:

```
> /discovery
```

En modo greenfield el planner hace preguntas abiertas; para un proyecto existente, también puede inferir respuestas desde el código (entidades desde `src/models/`, contenedores desde directorios top-level, dependencias desde `package.json`) y pedir confirmación. Eso produce docs que reflejan la realidad antes de entrar a `.claude/`.

Ver [Recorrido de discovery → Escenario 2](#escenario-2--docs-existentes-que-requieren-revisión).

**Notas importantes para brownfield:**
- **Discovery nunca edita `src/`.** Solo `docs/` y (después del intake) `.claude/`.
- **Elegir una primera feature de bajo riesgo** para validar el workflow:
  ```bash
  /feature Refactorizar tokens de auth para usar la nueva tabla de sesiones
  ```
- **Endurecer `gate_protected_areas`** para cualquier área que no debe auto-editarse (auth, billing, infra). El hook `gate-check.sh` forzará confirmación.
- **El CI/CD existente queda igual.** El framework solo agrega chequeos; no reemplaza el pipeline.

---

## Recorrido de discovery

### Escenario 1 — Proyecto completamente nuevo

Después de los pasos 1–4 de [Inicio rápido A](#a-proyecto-nuevo-desde-cero):

```
> /discovery
```

Qué pasa:

1. La skill prepara `docs/` y `docs/.discovery-state.md`.
2. Detecta que todas las fases son greenfield. Empieza en la **fase 1 (Visión)**.
3. El planner hace 1–3 preguntas focalizadas por turno — nunca dispara un draft completo de entrada.
4. El usuario responde; el planner propone un draft; el usuario lo redirige; el planner itera.
5. Cuando se confirma con `ok`, se escribe el archivo y se avanza a la fase 2.
6. Se repite a través de las fases 2–6.
7. La fase 7 (`/discovery-intake`) muestra el diff propuesto para `.claude/` y solo escribe con aprobación explícita.
8. Después del intake, el planner sugiere `/feature Bootstrap del scaffold según el plan C4`.

Un discovery completo desde cero suele tomar 2–4 sesiones. Se puede pausar en cualquier momento:

```
> pause
```

El estado se guarda. Se retoma con `/discovery resume`.

### Escenario 2 — Docs existentes que requieren revisión

Si ya existen requisitos, casos de uso, C4 o ADRs (en cualquier formato), copiar a `docs/` siguiendo la convención de [Estructura](#estructura), y luego:

```
> /discovery review --deep
```

El planner audita cada artefacto con tres lentes (completitud, consistencia interna, drift con el código) y presenta los hallazgos:

```
PHASE 5 — Architecture (Review)
✅ c4-context.md — sin issues
⚠️ c4-container.md — 2 issues:
   - Container "PaymentService" no está en src/, ¿deprecated?
   - Falta "NotificationWorker" (visto en src/workers/notify.ts)
❌ c4-component.md — no existe, recomendado para src/api/

¿Discutir en orden, o elegir uno (1/2/3)?
```

Se discute un issue a la vez. Cada issue resuelto actualiza la doc y el state file. Cuando todas las fases están limpias, `/discovery-intake` siembra `.claude/`.

### Escenario 3 — Trabajar una sola fase

No hace falta correr el pipeline completo. Cada fase es una skill standalone:

```
> /discovery-functional        # solo requisitos
> /discovery-architecture      # solo C4
> /discovery-decisions         # solo ADRs
```

Útil cuando ya hay un setup parcial y solo se quiere evolucionar una pieza. Las fases declaran sus dependencias — al editar FRs (fase 2), las fases 3 y 5 quedan marcadas como `partial` para recordar revisarlas después.

### Reglas que el planner respeta

- **Nada de generación silenciosa.** Toda escritura de doc se muestra como diff primero; solo se persiste con `ok` explícito.
- **Turnos chicos.** 1–3 preguntas por turno, nunca un cuestionario de 30 preguntas.
- **Review anclado en evidencia.** Cada issue cita un archivo o línea; nada de afirmaciones vagas.
- **Discovery nunca edita `src/`.** Solo `docs/` y `.discovery-state.md` hasta el intake.

---

## Comandos comunes

```bash
# Etapa 1 — diseño
/discovery                                                # pipeline completo (auto-modo)
/discovery review --deep                                  # re-auditar todas las fases vs código
/discovery <fase>                                         # saltar a una fase específica
/discovery resume                                         # retomar fase interrumpida

# Etapa 2 — construcción
/feature Agregar registro de usuarios con verificación    # texto libre → crea issue
/feature #42                                              # issue existente
/qa-test                                                  # QA completo (unit + E2E)
/research Comparar Redis vs Memcached
/audit src/auth                                           # auditoría de seguridad por path
/sync-schema                                              # forzar sync del modelo de datos
/prepare-commit                                           # validar readiness + draft de commit
```

---

## Qué editar por proyecto

| Archivo | Qué poner | Cuándo |
|---------|-----------|--------|
| `project.yml` | Dominio, invariantes, flujos críticos, áreas gate-protected | Setup (o auto-poblado por `/discovery-intake`) |
| `stack.yml` | Comandos de runtime, paths, config de schema, override opcional `docs:` | Setup |
| `memory/architecture.md` | Diseño del sistema, roles, patrones | Setup (o auto-poblado por `/discovery-intake`) |
| `docs/**` | Visión, requisitos, casos de uso, C4, ADRs | Continuamente, mediante `/discovery` |

Todo lo demás es genérico — agentes, skills, hooks, rules y CLAUDE.md no se editan por proyecto.

<details>
<summary>Ejemplos de configuración manual</summary>

**project.yml:**
```yaml
name: MiSaaS
description: Plataforma de gestión de inventarios
domain:
  language: es
  entities: [organization (tenant), user, warehouse, product, order]
tenant:
  enabled: true
  column: org_id
  isolation: rls
invariants:
  - name: Tenant Isolation
    rule: All DB queries filter by org_id.
    severity: critical
```

**stack.yml:**
```yaml
name: node-docker-prisma
runtime:
  exec_prefix: "docker compose exec api"
commands:
  test: "npx vitest run"
  lint: "npx eslint {path}"
  build: "npm run build"
schema:
  source: models
  paths: [prisma/schema.prisma]
```

</details>

---

## Extender

### Agregar un agent

```yaml
# .claude/agents/mi-agent.md
---
name: mi-agent
description: Cuándo invocar este agent.
model: sonnet              # opus | sonnet | haiku
tools: [Read, Grep, Bash]  # allowlist
disallowedTools: [Write]   # denylist (camelCase — requerido por Claude Code)
---
# Mi Agent
Instrucciones del rol.
```

> Los campos del frontmatter siguen la spec oficial de subagentes de Claude Code.
> `name` es requerido; `model` y `tools` son enforced por el runtime.

### Agregar una skill

```yaml
# .claude/skills/mi-skill/SKILL.md
---
name: mi-skill
description: Qué hace esta skill.
user-invocable: true
---
# /mi-skill
1. Paso uno
2. Paso dos
```

### MCP de base de datos

```yaml
# En stack.yml
database:
  type: "postgresql"
  mcp: true
  read_only: true
```

---

## Herramientas recomendadas

**[Claude Code Templates](https://github.com/davila7/claude-code-templates)** de **davila7** — el Analytics Dashboard (`npx claude-code-templates --analytics`) visualiza la actividad de los agentes y el uso de tokens.

---

## Licencia

Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.
