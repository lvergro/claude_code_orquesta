# <img src="assets/logo.png" alt="Orquesta Logo" width="50" height="50" align="center"/> Orquesta

**Sistema de orquestación de desarrollo para Claude Code.**

Orquesta convierte una sesión de Claude Code en un equipo de ingeniería disciplinado: un **arquitecto** que diseña, un **programador** que implementa, un **release manager** que commitea y un **validador QA** que prueba — cada uno con permisos enforced, memoria persistente compartida y un camino completamente trazable desde la idea hasta el PR mergeado.

**Una feature = un issue = un worktree = una rama = un PR.**

**[Read in English](README.md)**

---

## Tabla de contenidos

1. [¿Por qué Orquesta?](#por-qué-orquesta)
2. [Cómo funciona — los conceptos](#cómo-funciona--los-conceptos)
3. [Implementación — instálalo en tu proyecto](#implementación--instálalo-en-tu-proyecto)
4. [Primeros pasos: proyecto nuevo vs. existente](#primeros-pasos-proyecto-nuevo-vs-existente)
5. [Tutorial: de la idea al PR](#tutorial-de-la-idea-al-pr)
6. [Recorrido de discovery](#recorrido-de-discovery)
7. [Comandos del día a día](#comandos-del-día-a-día)
8. [Referencia de estructura](#referencia-de-estructura)
9. [Extender](#extender)
10. [FAQ](#faq)

---

## ¿Por qué Orquesta?

Trabajar un proyecto real con una sesión LLM pelada tiene modos de fallo predecibles. Orquesta existe para cerrar cada uno:

| Sin Orquesta | Con Orquesta |
|---|---|
| El contexto se evapora cuando el chat se compacta o la sesión termina | Todo el estado vive en **archivos** (`.claude/memory/`). Un hook de `SessionStart` re-inyecta el foco actual, así cada sesión arranca sabiendo qué estaba en curso |
| Un solo modelo hace todo — caro donde no hace falta, impredecible donde importa | **Agentes por rol con el modelo correcto para cada trabajo**: el planner hereda el modelo más fuerte de tu sesión, Sonnet construye (el grueso), Haiku commitea (barato, mecánico) |
| El asistente puede editar cualquier cosa, en cualquier momento | **Acceso a herramientas enforced**: el planner físicamente no puede ejecutar Bash, el agente git no puede editar archivos, y reglas `ask` nativas de permisos fuerzan confirmación antes de tocar rutas protegidas (migraciones, auth, billing…) |
| Cambios enormes e irreversibles sin rastro | Cada feature sigue **issue → spec → waves de tareas → commit por wave → PR**, con dos comentarios vivos en el issue documentando requisitos y ejecución |
| El trabajo en paralelo se pisa | Cada feature corre en un **git worktree aislado** — main queda limpio, las features no chocan |
| "¿Dónde íbamos?" después de cada interrupción | Todo pipeline es **reanudable**: re-ejecuta `/feature #42` y continúa desde el estado persistido, incluyendo tareas bloqueadas y CI pendiente |
| El diseño vive en la cabeza de alguien (o en una wiki desactualizada) | `/discovery` produce **docs de diseño canónicos** (requisitos, casos de uso, NFRs, C4, ADRs) en `docs/` *antes* del código, y deriva artefactos compactos de runtime desde ellos |

Y las meta-ventajas:

- **Stack-agnostic.** Los agentes nunca hardcodean comandos — leen `stack.yml`. Cambiar de Node a Python a cualquier-cosa-en-Docker es un cambio de un archivo.
- **Sin dependencias de runtime.** Archivos planos: markdown, YAML, bash, python3 y el CLI `gh`. Sin servidor, sin base de datos, sin build.
- **Tu CI/CD queda igual.** Orquesta agrega chequeos y proceso; nunca reemplaza tu pipeline.
- **Económico en tokens por diseño.** Los agentes cargan un resumen de arquitectura de ~30 líneas, no todo tu árbol de diseño. El detalle completo queda en `docs/` y se lee a demanda.

---

## Cómo funciona — los conceptos

### Dos etapas: diseñar y luego construir

```
                        ┌──────────────────────┐         ┌──────────────────────┐
   idea / brief  ─────► │ pipeline /discovery  │ ──────► │  pipeline /feature   │ ─────► PR
                        │ (artefactos diseño)  │         │ (issue → código → PR)│
                        └──────────────────────┘         └──────────────────────┘
                          docs/  +  .claude/                código  +  tests
```

- **`/discovery`** (se corre una vez por proyecto, se repite cuando el diseño evoluciona) te entrevista en turnos conversacionales cortos y produce documentos de diseño en `docs/`. Su fase final deriva la configuración compacta de runtime en `.claude/`.
- **`/feature`** (se corre por cada feature) toma un issue o una descripción en texto libre y la lleva por spec → implementación → tests → PR, commiteando wave por wave.

Puedes saltarte `/discovery` y configurar `.claude/` a mano — `/feature` funciona igual. Discovery es la forma de hacer el diseño *explícito y auditable* primero.

### Los cuatro agentes

Los subagentes se definen en `.claude/agents/*.md`. Su frontmatter `model`, `tools` y `disallowedTools` es **enforced por el runtime de Claude Code** — son permisos duros, no sugerencias:

| Agent | Rol | Modelo | Puede | No puede |
|-------|-----|--------|-------|----------|
| `planner` | Arquitecto + Investigador | `inherit`* | Leer, analizar, diseñar, escribir en `memory/` y `docs/` | Bash, código, commits |
| `builder` | Programador | `sonnet` | Escribir código, tests, ejecutar comandos | Push, editar áreas gate-protected |
| `git` | Release Manager | `haiku` | Commits y push | Edit/Write de cualquier archivo |
| `qa` | Validador QA | `sonnet` | Tests, automatización de browser, reportes | Editar código fuente (escrituras limitadas a artefactos QA + tests — por regla) |

\* `inherit` usa el modelo de tu sesión — en planes Max puedes fijarlo a `opus`; en Pro corre con el Sonnet de tu sesión, que es donde más rinde tu cuota.

Por qué importa:

- **Calidad:** el modelo que decide *qué* construir no se distrae con sintaxis; el modelo que construye (Sonnet) recibe un spec terminado.
- **Costo:** el modelo caro corre solo durante la planificación — y solo si tu plan lo incluye. El trabajo rutinario (commits, labels) corre en Haiku.
- **Seguridad:** un builder confundido igual no puede pushear; el agente git igual no puede reescribir tu código.

### Memoria persistente

El historial del chat nunca es la fuente de verdad. El estado vive en archivos:

| Archivo | Qué contiene | Quién lo escribe |
|---------|--------------|------------------|
| `.claude/memory/architecture.md` | Resumen ejecutivo de ~30 líneas del diseño | `/discovery-intake` (el C4 completo queda en `docs/architecture/`) |
| `.claude/memory/project-state.md` | Tareas activas, foco actual, blockers | planner (planes), builder (progreso) |
| `.claude/memory/requirements.md` | Índice FR↔UC, una línea por requisito | `/discovery-intake` |
| `.claude/memory/schema.md` | Snapshot compacto del modelo de datos | `/sync-schema` (auto-verificado al inicio de `/feature`) |
| `.claude/memory/research.md` | Log de investigación (problema → opciones → recomendación) | `/research` |
| `docs/**` | Diseño canónico: glosario, FRs, NFRs, UCs, C4, ADRs | Fases de `/discovery` (con tu aprobación) |

Una sola fuente de verdad por artefacto — `.claude/memory/` nunca duplica `docs/`, lo resume.

### Hooks y reglas de permisos — enforcement que el modelo no puede saltarse

Los hooks corren como shell scripts en eventos del ciclo de vida, fuera del control del modelo:

- **`auto-format.sh`** (`PostToolUse` en Edit/Write) — corre el formateador correcto (prettier, ruff/black, gofmt, rustfmt, shfmt, rubocop) sobre cada archivo modificado. Salta silenciosamente si no está instalado.
- **`session-context.sh`** (`SessionStart`) — inyecta las tareas activas y el foco actual desde `project-state.md`, así una sesión fresca sabe de inmediato qué hay en vuelo.

Las rutas protegidas usan el **sistema nativo de permisos** de Claude Code en vez de un hook propio: `gate_protected_areas` en `project.yml` es la fuente declarativa (patrón + razón), y `/discovery-intake` la compila a reglas `permissions.ask` en `settings.json` (`Edit(migrations/**)`, `Write(migrations/**)`…). El propio runtime pregunta antes de cualquier edición — sin script en el camino, nada que pueda fallar abierto. El CI verifica la paridad entre ambos archivos.

### Reglas por ruta

Las reglas en `.claude/rules/*.md` cargan **solo cuando se tocan archivos que matchean** — costo de contexto cero en caso contrario. Incluidas: `migrations.md` (expandir-luego-contraer, sin backfills síncronos, plan de rollback) y `tests.md` (testear comportamiento no internals, mockear en los bordes).

---

## Implementación — instálalo en tu proyecto

### Requisitos

| Herramienta | Para qué |
|-------------|----------|
| CLI de [Claude Code](https://claude.com/claude-code) | El runtime que todo orquesta |
| `git` | Worktrees, ramas, commits |
| CLI `gh` autenticado (`gh auth login`) | Issues, PRs, labels — toda la comunicación con GitHub |
| `python3` | Lo usan los hooks (parseo de JSON) |
| *(opcional)* `prettier`, `ruff`, `gofmt`… | El hook de auto-formato usa lo que esté instalado |

### Paso 1 — Copiar el framework

```bash
cd tu-proyecto
cp -r /ruta/a/claude-code-orquesta/.claude ./.claude
echo ".claude/settings.local.json" >> .gitignore
```

Commitea `.claude/` a git — es configuración compartida del equipo. Solo `settings.local.json` (permisos personales) queda fuera.

### Paso 2 — Decirle QUÉ es tu proyecto (`project.yml`)

`.claude/project.yml` define la identidad del proyecto. Deja que `/discovery` lo llene por ti (recomendado), o edítalo a mano:

```yaml
name: MiSaaS
description: Plataforma de gestión de inventarios

domain:
  language: es
  entities: [organization (tenant), user, warehouse, product, order]

# Multi-tenancy: si está habilitado, el builder exige la columna tenant en cada query
tenant:
  enabled: true
  column: org_id
  isolation: rls

# Reglas que NUNCA deben romperse. Los agentes paran y reportan si una se viola.
invariants:
  - name: Tenant Isolation
    rule: All DB queries filter by org_id. No cross-tenant data leaks.
    severity: critical

# Rutas donde una regla ask nativa fuerza confirmación antes de editar
gate_protected_areas:
  - pattern: "migrations/"
    reason: Schema changes require careful planning
  - pattern: "auth/**"
    reason: Authentication logic
```

Qué te da cada sección:

- **`entities`** — vocabulario compartido; el planner usa estos nombres en los specs.
- **`tenant`** — si está habilitado, "filtrar por tenant" pasa a ser regla enforced para el builder, no una esperanza.
- **`invariants`** — los chequea el planner en los specs y `/validate-invariants`; una violación crítica detiene el pipeline.
- **`gate_protected_areas`** — el único mecanismo entre una edición apresurada y tu carpeta de migraciones. Se declara aquí (patrón + razón) y se aplica como reglas `permissions.ask` nativas en `settings.json` — `/discovery-intake` las compila, o agrega las reglas `Edit(patrón)`/`Write(patrón)` a mano.

### Paso 3 — Decirle CÓMO ejecutar las cosas (`stack.yml`)

`.claude/stack.yml` es el único lugar donde viven los comandos. Los agentes referencian `{stack.commands.test}` etc. — nunca hardcodean:

```yaml
name: node-docker-prisma

runtime:
  exec_prefix: "docker compose exec api"   # prefijo de TODO comando de runtime ("" si no aplica)

commands:
  install: "npm install"
  test: "npx vitest run"
  test_single: "npx vitest run {file}"
  lint: "npx eslint {path}"
  type_check: "npx tsc --noEmit"
  build: "npm run build"
  dev: "npm run dev"

paths:
  source: "src/"
  tests: "tests/"

conventions:
  test_file_pattern: "{name}.test.ts"

# Opcional: mantener memory/schema.md sincronizado con tu modelo de datos real
schema:
  source: models
  paths: [prisma/schema.prisma]
```

El bloque `schema` habilita la auto-verificación: cada corrida de `/feature` chequea si el snapshot está desactualizado y re-sincroniza antes de planificar.

### Paso 4 — Integraciones opcionales

**Tracker de issues (modelo híbrido).** El diseño queda en `docs/`, el estado vive en tu tracker:

```yaml
# stack.yml
tracker:
  type: linear        # linear | github | none
```

Con tracker configurado, `/discovery-intake` espeja cada requisito funcional aprobado como issue padre, y `/feature FR-01` crea el issue de implementación debajo. `linear` usa el servidor MCP de Linear; `github` usa el CLI `gh` directamente.

**MCP de base de datos.** Deja que el planner inspeccione el schema real en vez de confiar en docs:

```yaml
# stack.yml
database:
  type: "postgresql"
  mcp: true
  read_only: true
```

### Paso 5 — Verificar

Abre `claude` en el repo y comprueba que:

1. `/discovery`, `/feature`, `/qa-test` aparecen en la lista de skills (escribe `/`).
2. Editar un archivo bajo `migrations/` dispara la confirmación del gate.
3. `cat .claude/memory/project-state.md` muestra la plantilla idle.

Listo, está instalado.

---

## Primeros pasos: proyecto nuevo vs. existente

### A. Proyecto nuevo (greenfield)

```bash
mkdir mi-saas && cd mi-saas
git init
cp -r /ruta/a/claude-code-orquesta/.claude ./.claude
echo ".claude/settings.local.json" >> .gitignore
claude
```

Luego:

```
> /discovery
```

`/discovery` recorre 7 fases (visión → requisitos → casos de uso → NFRs → C4 → ADRs → intake), un turno conversacional a la vez. La fase final siembra `project.yml` y `memory/architecture.md` para que `/feature` tenga una fuente de verdad real.

Cuando el intake termina, el planner sugiere la primera feature — típicamente el scaffold:

```
> /feature Bootstrap del proyecto — scaffold Next.js + Supabase + Prisma
```

### B. Proyecto existente (brownfield)

Misma instalación, distinto primer comando. El objetivo es enseñarle al framework lo que ya existe, no regenerarlo.

**B.1 — Ya tienes docs de diseño** (Notion, Confluence, markdown): cópialos a `docs/` siguiendo la [estructura](#referencia-de-estructura), y luego:

```
> /discovery review --deep
```

El planner audita cada artefacto (completitud, consistencia interna, drift contra el código real) y recorre los hallazgos uno por uno. Cuando todo está limpio, `/discovery-intake` siembra `.claude/`.

**B.2 — Aún no hay docs de diseño:**

```
> /discovery
```

Para un código existente, el planner infiere respuestas desde el código (entidades desde los modelos, contenedores desde los directorios top-level, dependencias desde `package.json`) y te pide confirmar — produciendo docs que reflejan la realidad antes de llegar a `.claude/`.

**Notas de seguridad para brownfield:**

- **Discovery nunca edita `src/`.** Solo `docs/` y (después del intake) `.claude/`.
- **Elige una primera feature de bajo riesgo** para validar el workflow de punta a punta.
- **Endurece `gate_protected_areas`** alrededor de lo que no quieres que se auto-edite (auth, billing, infra).
- **El CI/CD existente queda intacto.**

---

## Tutorial: de la idea al PR

Esto es lo que pasa realmente cuando corres una feature. Digamos que quieres exportar a CSV una lista de pedidos:

```
> /feature Agregar export CSV a la lista de pedidos
```

**Fase 0 — Chequeo de resume.** Verifica `gh auth`, chequea si `schema.md` está desactualizado (re-sincroniza si lo está) y busca un worktree existente para esta feature. Si lo encuentra, una corrida anterior fue interrumpida — retoma en vez de empezar de cero.

**Fase 1 — Intake.** Crea el issue de GitHub `#57 "Agregar export CSV a la lista de pedidos"` y le pone label (`enhancement`). Si hubieras pasado `#42` o una URL de issue, lee el issue existente. Si pasaste `FR-03`, trae el bloque completo de ese requisito desde `docs/requirements/functional.md` como criterios de aceptación incorporados.

**Fase 2 — Spec. El único gate de aprobación del pipeline.** El planner lee `architecture.md`, los ADRs relevantes y tus invariantes, y produce:

```
Alcance: Agregar una acción "Exportar CSV" a la lista de pedidos que
descarga la vista filtrada actual como CSV.

Criterios de aceptación:
- GET /api/orders/export respeta los mismos filtros que la vista de lista
- El export respeta el aislamiento por org_id (invariante: Tenant Isolation)
- Un export de 10k filas completa en < 5s

Tareas:
  Wave 1 — Backend: endpoint, serializador CSV, reutilización de filtros
  Wave 2 — UI: botón de export, manejo de descarga, estado de carga
  Wave 3 — Tests: unit del serializador, integración del endpoint

Archivos: src/api/orders/export.ts, src/components/OrdersToolbar.tsx, ...
Estrategia de tests: ...

¿Proceder con la implementación? (yes/no)
```

Dices `yes` (o `no` — nada se ha creado aún más allá del issue). Con el yes, se postean dos comentarios al issue: **Requirements** (inmutable) y **Execution Plan** (checklist vivo, actualizado por ID después de cada wave).

**Fase 3 — Worktree.** Crea un checkout aislado en `../.worktrees/feat/57-agregar-export-csv...` en la rama `feat/57-…`, partiendo de `origin/main` fresco. Tu checkout principal no se toca de aquí en adelante.

**Fase 4 — Ejecución.** El builder (Sonnet) implementa tarea por tarea: escribir → testear → marcar hecha. Después de **cada wave**: commit (el estado de memoria queda excluido), fetch + rebase sobre main si avanzó, y actualización del comentario de Execution:

```
✅ 1 Agregar endpoint GET /api/orders/export
✅ 2 Reutilizar filtros de la lista en la query de export
✅ 3 Serializador CSV en streaming
→ commit: feat(57-agregar-export-csv): wave 1 — endpoint de export
```

Si una tarea falla 3 veces, se postea un comentario de blocker al issue y el pipeline para con el estado guardado. El próximo `/feature #57` pregunta "Blocker: … ¿Resuelto?" y continúa.

**Fase 5 — Integración.** Validación completa (tests + build), una pasada de code review limitada al diff de la rama (los hallazgos críticos se postean al issue), push, y un **PR en draft**:

```
Closes #57
## Summary / ## Changes / ## Test plan / ## Code Review
```

Luego observa el CI (tope de 10 minutos). Verde → el PR pasa a **ready for review** automáticamente. Rojo → se postea un comentario de fallo y el PR queda en draft; re-correr `/feature #57` re-chequea.

**Fase 6 — Cleanup.** El estado se archiva en `.claude/memory/archive/`, el status final queda en el comentario de Execution, y recibes:

```
✅ Feature #57 entregada. PR: https://github.com/tu/repo/pull/58 — mergea cuando quieras.
```

Mergear es **tuyo** — Orquesta nunca mergea. Después de mergear, recupera disco:

```
> /cleanup-worktrees
```

Lista los worktrees cuyos PRs se mergearon/cerraron, pregunta una vez, y los elimina (nunca `--force`).

**¿Features en paralelo?** Abre otra terminal y corre `/feature #61`. Cada worktree está completamente aislado.

---

## Recorrido de discovery

### Escenario 1 — Proyecto completamente nuevo

```
> /discovery
```

1. Prepara `docs/` y `docs/.discovery-state.md`.
2. Detecta que todas las fases son greenfield; empieza en la **fase 1 (Visión)**.
3. El planner hace 1–3 preguntas focalizadas por turno — nunca te tira un draft completo de entrada.
4. Respondes; propone un draft; lo rediriges; itera.
5. Con tu `ok` explícito, se escribe el archivo y avanzas.
6. Se repite por las fases 2–6. La fase 7 muestra el diff propuesto para `.claude/` y escribe solo con aprobación.

Un discovery completo desde cero suele tomar 2–4 sesiones. `pause` en cualquier momento; `/discovery resume` continúa.

### Escenario 2 — Docs existentes que requieren revisión

```
> /discovery review --deep
```

El planner audita cada artefacto con tres lentes (completitud, consistencia interna, drift con el código) y presenta hallazgos:

```
PHASE 5 — Architecture (Review)
✅ c4-context.md — sin issues
⚠️ c4-container.md — 2 issues:
   - Container "PaymentService" no está en src/, ¿deprecated?
   - Falta "NotificationWorker" (visto en src/workers/notify.ts)
❌ c4-component.md — no existe, recomendado para src/api/

¿Discutir en orden, o elegir uno (1/2/3)?
```

Un issue a la vez; cada resolución actualiza la doc y el state file.

### Escenario 3 — Trabajar una sola fase

Cada fase es una skill standalone:

```
> /discovery-functional        # solo requisitos
> /discovery-architecture      # solo C4
> /discovery-decisions         # solo ADRs
```

Las fases declaran dependencias — editar FRs (fase 2) marca las fases 3 y 5 como `partial` para recordarte revisarlas.

### Reglas que el planner siempre respeta

- **Nada de generación silenciosa.** Toda escritura de doc se muestra como diff primero; se persiste solo con `ok` explícito.
- **Turnos cortos.** 1–3 preguntas, nunca un cuestionario de 30.
- **Review anclado en evidencia.** Cada issue cita un archivo o línea.
- **Discovery nunca edita `src/`.**

---

## Comandos del día a día

```bash
# Etapa 1 — diseño
/discovery                                                # pipeline completo (auto-modo)
/discovery review --deep                                  # re-auditar todas las fases vs código
/discovery <fase>                                         # saltar a una fase específica
/discovery resume                                         # retomar fase interrumpida

# Etapa 2 — construcción
/feature Agregar registro de usuarios con verificación    # texto libre → crea issue
/feature #42                                              # issue existente
/feature FR-03                                            # implementar un requisito funcional
/qa-test                                                  # QA completo (unit + E2E en browser)
/research Comparar Redis vs Memcached                     # investigación → research.md
/audit src/auth                                           # auditoría de seguridad por path
/sync-schema                                              # forzar sync del modelo de datos
/prepare-commit                                           # validar readiness + draft de commit
/cleanup-worktrees                                        # eliminar worktrees con PR mergeado
```

---

## Referencia de estructura

```
.claude/
├── CLAUDE.md                           # Entry point — importa project.yml + stack.yml
├── project.yml                         # QUÉ: dominio, invariantes, áreas gate-protected
├── stack.yml                           # CÓMO: runtime, comandos, paths, fuente de schema
│
├── settings.json                       # Compartido: permisos (deny/ask), hooks
├── settings.local.json                 # Personal/local: allows extra (gitignored)
│
├── hooks/                              # Hooks de ciclo de vida (corren como shell scripts)
│   ├── auto-format.sh                  #   PostToolUse Edit|Write — formatea el archivo modificado
│   └── session-context.sh              #   SessionStart — inyecta Current Focus de project-state
│
├── rules/                              # Reglas por ruta (cargan solo al tocar archivos matching)
│   ├── migrations.md                   #   paths: migrations/**, prisma/schema.prisma
│   └── tests.md                        #   paths: **/*.test.*, tests/**
│
├── agents/                             # Subagentes — model + tools enforced via frontmatter
│   ├── planner.md                      #   model: inherit — diseña, nunca codea
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
│   ├── discovery-intake/SKILL.md       #     fase 7: docs/ → .claude/ (+ sync de tracker)
│   │  # ── Build (etapa 2) ──
│   ├── feature/SKILL.md                #   /feature — pipeline principal de construcción
│   ├── qa-test/SKILL.md                #   /qa-test — validación QA E2E
│   ├── research/SKILL.md               #   /research — investigación técnica
│   ├── audit/SKILL.md                  #   /audit — auditoría de seguridad
│   ├── sync-schema/SKILL.md            #   /sync-schema — sync del modelo de datos
│   ├── prepare-commit/SKILL.md         #   /prepare-commit
│   ├── validate-invariants/SKILL.md    #   Chequeos de seguridad
│   ├── write-tests/SKILL.md            #   Estrategia de tests
│   ├── analyze-architecture/SKILL.md   #   Detección de drift
│   ├── archive-state/SKILL.md          #   Ciclo de vida del estado
│   └── cleanup-worktrees/SKILL.md      #   /cleanup-worktrees — elimina worktrees mergeados
│
└── memory/                             # Estado runtime compacto — derivado de docs/, sin duplicar
    ├── architecture.md                 #   Resumen ejecutivo, ~30 líneas (C4 completo en docs/architecture/)
    ├── requirements.md                 #   Índice FR↔UC (una línea por FR)
    ├── schema.md                       #   Modelo de datos (auto-sync desde stack.yml)
    ├── project-state.md                #   Tareas activas + Current Focus + Blockers
    ├── research.md                     #   Log de investigación
    └── archive/                        #   Estados completados
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

### Qué editar por proyecto

| Archivo | Qué poner | Cuándo |
|---------|-----------|--------|
| `project.yml` | Dominio, invariantes, flujos críticos, áreas gate-protected | Setup (o auto-poblado por `/discovery-intake`) |
| `stack.yml` | Comandos de runtime, paths, config de schema, tracker | Setup |
| `memory/architecture.md` | Resumen del diseño del sistema | Setup (o auto-poblado por `/discovery-intake`) |
| `docs/**` | Visión, requisitos, casos de uso, C4, ADRs | Continuamente, mediante `/discovery` |

Todo lo demás es genérico — agentes, skills, hooks, rules y CLAUDE.md no se editan por proyecto.

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

## FAQ

**¿Tengo que correr `/discovery` antes de `/feature`?**
No. `/feature` funciona con un `project.yml` + `architecture.md` escritos a mano. Discovery es la forma recomendada de hacer el diseño explícito, trazable y auditable — especialmente en equipo.

**¿Mergea mis PRs?**
Nunca. Orquesta entrega un PR revisado y con CI verde, y se detiene. Mergear — y el criterio que implica — es tuyo.

**¿Cuánto cuesta correrlo?**
El planner hereda el modelo de tu sesión (fija Opus solo si tu plan lo incluye); el grueso del trabajo corre en Sonnet y los pasos mecánicos en Haiku. El modelo de memoria (resúmenes compactos, reglas por ruta, docs a demanda) mantiene el contexto por turno pequeño. En una cuenta Pro este default es la configuración más barata que preserva el proceso.

**¿Funciona sin GitHub?**
El pipeline `/feature` depende de `gh` para issues y PRs. Discovery, la memoria, los hooks y el resto de skills funcionan sin él.

**¿Puedo proteger más áreas después de instalar?**
Sí — agrega el patrón a `gate_protected_areas` en `project.yml` y las reglas `Edit(patrón)`/`Write(patrón)` a `permissions.ask` en `settings.json` (o re-corre `/discovery-intake`, que las compila por ti). El CI verifica que ambos archivos queden en sync.

**¿Qué pasa si mi sesión muere a mitad de una feature?**
No se pierde nada. El estado está en disco y en los comentarios del issue. `/feature #N` retoma desde la fase, tarea y blocker exactos donde paró.

---

## Herramientas recomendadas

**[Claude Code Templates](https://github.com/davila7/claude-code-templates)** de **davila7** — el Analytics Dashboard (`npx claude-code-templates --analytics`) visualiza la actividad de los agentes y el uso de tokens.

---

## Licencia

Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## Orquesta Studio

Un dashboard web local sin base de datos para proyectos Orquesta. Proporciona un visor de documentación, un tablero kanban respaldado por GitHub y un inspector del estado del pipeline — sin introducir ningún almacén de datos nuevo.

### Instalación

```bash
cd tu-proyecto
pip install -r tools/dashboard/requirements.txt
```

### Ejecución

```bash
bash tools/dashboard/run.sh           # puerto por defecto 8765
bash tools/dashboard/run.sh --port 9000
bash tools/dashboard/run.sh --read-only   # deshabilita todos los endpoints de escritura
```

Abre [http://localhost:8765](http://localhost:8765).

### Pestañas

| Pestaña | Qué muestra | ¿Escribe? |
|---------|-------------|-----------|
| **Docs** | `docs/` y `.claude/memory/` renderizados como HTML con diagramas Mermaid | No |
| **Backlog** | Issues de GitHub como tablero kanban (Backlog / Ready / In Progress / Done) | Sí — vía CLI `gh` |
| **State** | Fase del pipeline actual, tareas activas, worktrees | No |

### Cómo funciona

- **Sin base de datos.** Las columnas del kanban se derivan en tiempo real del estado de los issues de GitHub y las ramas locales. No se almacena nada localmente.
- **Usa tu `gh auth`.** Crear o mover tareas queda atribuido a tu cuenta de GitHub — igual que ejecutar `gh issue create` manualmente.
- **Uso en equipo.** Cada miembro del equipo ejecuta su propia instancia. El estado compartido vive en GitHub.
- **Modo solo lectura.** Usa `--read-only` para deshabilitar todas las escrituras (ideal para pantallas de visualización o instancias compartidas).
