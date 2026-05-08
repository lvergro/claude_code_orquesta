# <img src="assets/logo.png" alt="Orquesta Logo" width="50" height="50" align="center"/> Orquesta

**Sistema de orquestacion de desarrollo para Claude Code.**

Sistema de orquestacion basado en archivos que estructura como Claude Code planifica, implementa y entrega features — usando roles de subagentes, memoria persistente y workflows orientados a issues.

**Un feature = un issue = un worktree = un branch = un PR.**

**[Read in English](README.md)** | Disponible para **[Antigravity (Gemini)](antigravity/)**

---

## Como Funciona

Cuatro subagentes con acceso a herramientas **enforced** (via `tools` / `disallowedTools` en frontmatter), despachados automaticamente:

| Agent | Rol | Modelo | Puede | No puede |
|-------|-----|--------|-------|----------|
| `planner` | Arquitecto + Investigador | `opus` | Leer, analizar, disenar, escribir en memory/ | Bash, codigo, commits |
| `builder` | Programador | `sonnet` | Escribir codigo, tests, correr comandos | Push, editar areas gate-protected |
| `git` | Release Manager | `haiku` | Commits y push | Edit/Write de cualquier archivo |
| `qa` | Validador QA | `sonnet` | Tests, automatizacion de browser, reportes | (sin restriccion de edit aun — por convencion) |

Un workflow principal (`/feature`) los orquesta a traves de un pipeline:

```
/feature #42  (o descripcion en texto libre)

PHASE 0 → Sync de schema + verificacion de resume
PHASE 1 → Intake (crear/leer issue de GitHub, auto-label)
PHASE 2 → Spec (planner: alcance, criterios de aceptacion, tareas en waves)
PHASE 3 → Setup de worktree (branch + directorio aislado)
PHASE 4 → Ejecucion (builder: implementar + testear cada tarea, commit por wave)
PHASE 5 → Integracion (validar, push, crear PR)
PHASE 6 → Cleanup (archivar estado)
```

Se interrumpio? Ejecuta `/feature #42` de nuevo — retoma desde donde quedo.

Features en paralelo? Multiples terminales, cada una con un `/feature #N` diferente. Cada worktree esta completamente aislado.

---

## Estructura

```
.claude/
├── CLAUDE.md                          # Entry point — importa project.yml + stack.yml
├── project.yml                        # QUE: dominio, invariantes, areas gate-protected
├── stack.yml                          # COMO: runtime, comandos, paths, fuente de schema
│
├── settings.json                      # Compartido: permisos (deny/ask), hooks
├── settings.local.json                # Personal/local: allows extra (gitignoreable)
│
├── hooks/                             # Hooks de ciclo de vida (corren como shell scripts)
│   ├── gate-check.sh                  #   PreToolUse Edit|Write — bloquea gate_protected_areas
│   └── session-context.sh             #   SessionStart — inyecta Current Focus de project-state
│
├── rules/                             # Reglas con paths (cargan solo al tocar files matching)
│   ├── migrations.md                  #   paths: migrations/**, prisma/schema.prisma
│   └── tests.md                       #   paths: **/*.test.*, tests/**
│
├── agents/                            # Subagentes — model + tools enforced via frontmatter
│   ├── planner.md                     #   model: opus  — disena, nunca codea
│   ├── builder.md                     #   model: sonnet — codea silencioso
│   ├── git.md                         #   model: haiku — commits + push
│   └── qa.md                          #   model: sonnet — tests + browser E2E
│
├── skills/                            # Workflows (slash commands)
│   ├── feature/SKILL.md               #   /feature — pipeline principal
│   ├── qa-test/SKILL.md               #   /qa-test — validacion QA E2E
│   ├── research/SKILL.md              #   /research — investigacion tecnica
│   ├── audit/SKILL.md                 #   /audit — auditoria de seguridad
│   ├── sync-schema/SKILL.md           #   /sync-schema — sync del modelo de datos
│   ├── prepare-commit/SKILL.md        #   /prepare-commit
│   ├── validate-invariants/SKILL.md   #   Chequeos de seguridad
│   ├── summarize-context/SKILL.md     #   Compresion de contexto
│   ├── write-tests/SKILL.md           #   Estrategia de tests
│   ├── analyze-architecture/SKILL.md  #   Deteccion de drift
│   └── archive-state/SKILL.md         #   Ciclo de vida del estado
│
└── memory/                            # Estado persistente — fuentes de verdad cross-sesion
    ├── architecture.md                #   Diseno del sistema
    ├── schema.md                      #   Modelo de datos (auto-sync desde stack.yml)
    ├── project-state.md               #   Active Tasks + Current Focus + Blockers
    ├── research.md                    #   Log de investigacion
    ├── decisions/                     #   ADRs (DEC-*.md)
    └── archive/                       #   Estados completados
```

---

## Inicio Rapido

Dos caminos: **A. Proyecto nuevo** (greenfield) o **B. Proyecto con avance** (brownfield).

### A. Proyecto nuevo desde cero

Para un proyecto que no existe aun, o que no tiene codigo en produccion.

```bash
# 1. Crear el proyecto + repo git
mkdir mi-saas && cd mi-saas
git init

# 2. Copiar el framework
cp -r /ruta/a/claude-code-orquesta/.claude ./.claude

# 3. (Opcional) ignorar tu settings local
echo ".claude/settings.local.json" >> .gitignore

# 4. Abrir Claude Code
claude
```

Pedile a Claude que configure el framework con tu dominio y stack:

```
Configura el directorio .claude/ para un proyecto nuevo.

Dominio: [ej: "SaaS multi-tenant para inventario de restaurantes"]
Stack: [ej: "Next.js 14 + Supabase + Prisma, corre en Docker"]
Entidades: [ej: "organization (tenant), user, restaurant, menu, order"]
Multi-tenant: [si — RLS con columna org_id / no]

Invariantes clave:
- [ej: "Todas las queries de DB filtran por org_id"]
- [ej: "Totales de pedidos se recalculan en el servidor"]

Flujos criticos:
- [ej: "Pedido: validar menu → verificar stock → cobrar → notificar cocina"]

Areas gate-protegidas (confirmacion extra antes de editar):
- migrations/
- [ej: src/auth/]

Actualiza project.yml, stack.yml y memory/architecture.md desde este brief.
No toques skills, agents, hooks ni CLAUDE.md.
```

Despues lanza tu primer feature:

```bash
/feature Bootstrap del proyecto — scaffold Next.js + Supabase + Prisma
```

El `planner` produce el spec, el `builder` lo ejecuta tarea por tarea,
y el `git` hace commit por wave.

---

### B. Proyecto con avance (brownfield)

Para un proyecto que ya tiene codigo, tests e historia en produccion.
El objetivo es **enseñarle al framework lo que ya existe**, no regenerarlo.

```bash
# 1. Desde la raiz del proyecto
cp -r /ruta/a/claude-code-orquesta/.claude ./.claude

# 2. Agregar settings.local al gitignore (opcional)
echo ".claude/settings.local.json" >> .gitignore

# 3. Abrir Claude Code en el repo
claude
```

Pedile a Claude que **descubra** lo que ya existe en lugar de inventarlo:

```
Este es un proyecto existente. Configura .claude/ leyendo el codigo, no adivinando.

Pasos:
1. Corre /init para escanear el repo y detectar comandos build/test/lint.
2. Llena stack.yml desde package.json / pyproject.toml / Dockerfile.
   - Detecta exec_prefix (Docker? bare metal?)
   - Detecta comandos test, lint, type_check, build, dev
   - Detecta fuente de schema (Prisma? migraciones? SQL plano?) y configura schema.paths
3. Llena project.yml:
   - Inferi entidades de dominio desde src/models/ o el schema de DB
   - Inferi estrategia multi-tenant desde queries existentes (busca columnas tenant_id / org_id)
   - Agrega gate_protected_areas para migrations/, auth/, payment/, y cualquier directorio sensible
4. Llena memory/architecture.md desde la estructura real de src/.
   Referenciando archivos reales, no aspiracionales.
5. Corre /sync-schema para poblar memory/schema.md desde los modelos reales.
6. Pausa para revision. Mostrame el diff antes de continuar.
```

Notas importantes para brownfield:
- **No dejes que Claude reescriba tu codigo** durante el setup. El setup solo edita `.claude/`.
- **Elegi un primer feature de bajo riesgo** para validar el workflow:
  ```bash
  /feature Refactorizar tokens de auth para usar la nueva tabla de sesiones
  ```
- **Endurece `gate_protected_areas`** para cualquier zona que no quieras auto-editable (auth, billing, infra). El hook `gate-check.sh` forzara confirmacion.
- **Tu CI/CD se queda como esta.** El framework agrega chequeos, no reemplaza tu pipeline.

---

### Comandos comunes

```bash
/feature Agregar registro de usuarios con verificacion por email   # texto libre → crea issue
/feature #42                                                       # issue existente
/qa-test                                                           # QA completo (unit + E2E)
/research Comparar Redis vs Memcached
/audit src/auth                                                    # auditoria de seguridad por path
/sync-schema                                                       # forzar sync del modelo de datos
/prepare-commit                                                    # validar readiness + draft de commit
```

---

## Que Editar por Proyecto

| Archivo | Que poner | Cuando |
|---------|-----------|--------|
| `project.yml` | Dominio, invariantes, flujos criticos | Setup |
| `stack.yml` | Comandos de runtime, paths, config de schema | Setup |
| `memory/architecture.md` | Diseno del sistema, roles, patrones | Setup + evoluciona |

El resto es generico — agents, skills y CLAUDE.md no se editan.

<details>
<summary>Ejemplos de configuracion manual</summary>

**project.yml:**
```yaml
name: MiSaaS
description: Plataforma de gestion de inventarios
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
description: Cuando invocar este agent.
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
description: Que hace esta skill.
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

## Herramientas Recomendadas

**[Claude Code Templates](https://github.com/davila7/claude-code-templates)** de **davila7** — el Analytics Dashboard (`npx claude-code-templates --analytics`) visualiza la actividad de los agentes y el uso de tokens.

---

## Licencia

Licencia MIT. Ver [LICENSE](LICENSE) para mas detalles.
