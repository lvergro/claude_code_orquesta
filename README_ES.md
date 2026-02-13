# <img src="assets/logo.png" alt="Orquesta Logo" width="50" height="50" align="center"/> Orquesta

**Sistema de orquestacion de desarrollo para Claude Code.**

Sistema de orquestacion basado en archivos que estructura como Claude Code planifica, implementa y entrega features — usando roles de subagentes, memoria persistente y workflows orientados a issues.

**Un feature = un issue = un worktree = un branch = un PR.**

**[Read in English](README.md)** | Disponible para **[Antigravity (Gemini)](antigravity/)**

---

## Como Funciona

Tres subagentes con acceso restringido a herramientas, despachados automaticamente:

| Agent | Rol | Modelo | Puede | No puede |
|-------|-----|--------|-------|----------|
| `planner` | Arquitecto + Investigador | opus | Leer, analizar, disenar, escribir en memory/ | Codigo, commits, Bash |
| `builder` | Programador + QA | sonnet | Escribir codigo, tests, ejecutar comandos | Editar arquitectura, commits |
| `git` | Release Manager | haiku | Commits y push | Escribir codigo o editar archivos |

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
├── CLAUDE.md                          # Entry point
├── project.yml                        # QUE: dominio, invariantes, flujos criticos
├── stack.yml                          # COMO: runtime, comandos, paths
├── models.yml                         # Routing de modelos (haiku/sonnet/opus)
├── settings.local.json                # Permisos de herramientas
│
├── agents/                            # Subagentes (dispatch nativo)
│   ├── planner.md
│   ├── builder.md
│   └── git.md
│
├── skills/                            # Workflows
│   ├── feature/SKILL.md               #   /feature — pipeline principal
│   ├── research/SKILL.md              #   /research — investigacion tecnica
│   ├── audit/SKILL.md                 #   /audit — auditoria de seguridad
│   ├── sync-schema/SKILL.md           #   /sync-schema — sync del modelo de datos
│   ├── prepare-commit/SKILL.md        #   /prepare-commit
│   ├── validate-invariants/SKILL.md   #   Chequeos de seguridad (auto)
│   ├── summarize-context/SKILL.md     #   Compresion de contexto (auto)
│   ├── write-tests/SKILL.md           #   Estrategia de tests (auto)
│   ├── analyze-architecture/SKILL.md  #   Deteccion de drift (auto)
│   └── archive-state/SKILL.md         #   Ciclo de vida del estado (auto)
│
└── memory/                            # Estado persistente
    ├── architecture.md                #   Diseno del sistema (fuente de verdad)
    ├── schema.md                      #   Modelo de datos (auto-sincronizado)
    ├── project-state.md               #   Tareas activas + progreso
    ├── research.md                    #   Log de investigacion
    ├── decisions/                     #   Registros de decisiones arquitectonicas
    └── archive/                       #   Estados completados
```

---

## Inicio Rapido

### 1. Copiar el framework

```bash
cp -r /ruta/al/framework/.claude/ ./.claude/
```

### 2. Dejar que Claude configure tu proyecto

```bash
claude
```

```
Configura el directorio .claude/ de este proyecto.
Es un [describe tu proyecto — ej: "SaaS multi-tenant para gestion de restaurantes"].

Stack: [ej: "Next.js 14 + Supabase + Prisma, corriendo en Docker"]
Entidades: [ej: "organizaciones, usuarios, restaurantes, menus, pedidos"]
Multi-tenant: [si/no — ej: "si, RLS con columna org_id"]

Invariantes clave:
- [ej: "Todas las queries deben filtrar por org_id"]
- [ej: "Totales de pedidos recalculados en el servidor"]

Flujos criticos:
- [ej: "Pedido: validar menu → verificar disponibilidad → crear pedido → notificar cocina"]

Lee project.yml, stack.yml y memory/architecture.md, y llenalos.
```

Claude llena `project.yml`, `stack.yml` y `architecture.md` alineados a tu dominio.

### 3. Empezar a construir

```bash
/feature Agregar registro de usuarios con verificacion por email
/feature #42                    # issue existente
/research Comparar Redis vs Memcached
/audit src/auth
/sync-schema                    # forzar sync del modelo de datos
```

---

## Que Editar por Proyecto

| Archivo | Que poner | Cuando |
|---------|-----------|--------|
| `project.yml` | Dominio, invariantes, flujos criticos | Setup |
| `stack.yml` | Comandos de runtime, paths, config de schema | Setup |
| `models.yml` | Routing de modelos (haiku/sonnet/opus) | Setup o ajuste de costos |
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
description: Cuando invocar este agent.
allowed-tools: [Read, Grep, Bash]
disallowed-tools: [Write]
---
# Mi Agent
Instrucciones del rol.
```

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

Uso libre. Adaptalo a tu proyecto.
