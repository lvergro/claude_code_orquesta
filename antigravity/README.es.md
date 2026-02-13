# Orquesta para Antigravity

**Sistema de orquestacion de desarrollo para [Antigravity](https://antigravity.google).**

Sistema de orquestacion basado en archivos que estructura como el agente de IA planifica, implementa y entrega features — usando memoria persistente y workflows orientados a issues. Adaptado del original para Claude Code para funcionar con las convenciones nativas del directorio `.agent/` de Antigravity.

**Un feature = un issue = un worktree = un branch = un PR.**

---

## Como Funciona

Un workflow principal (`/feature`) orquesta al agente a traves de un pipeline:

```
/feature #42  (o descripcion en texto libre)

PHASE 0 → Sync de schema + verificacion de resume
PHASE 1 → Intake (crear/leer issue de GitHub, auto-label)
PHASE 2 → Spec (alcance, criterios de aceptacion, tareas en waves)
PHASE 3 → Setup de worktree (branch + directorio aislado)
PHASE 4 → Ejecucion (implementar + testear cada tarea, commit por wave)
PHASE 5 → Integracion (validar, push, crear PR)
PHASE 6 → Cleanup (archivar estado)
```

Se interrumpio? Ejecuta `/feature #42` de nuevo — retoma desde donde quedo.

Features en paralelo? Multiples terminales, cada una con un `/feature #N` diferente. Cada worktree esta completamente aislado.

---

## Estructura

```
GEMINI.md                              ← Entry point (siempre cargado)
.agent/
  rules/                               ← Siempre cargadas en contexto
    project.md                         ← Dominio, invariantes, flujos criticos
    stack.md                           ← Comandos de runtime y paths
    conventions.md                     ← Estandares de codigo y git
  workflows/                           ← Invocados por el usuario con /
    feature.md                         ← /feature (issue → PR)
    research.md                        ← /research
    audit.md                           ← /audit
    prepare-commit.md                  ← /prepare-commit
  skills/                              ← Auto-activados por el agente
    validate-invariants/SKILL.md       ← Chequeos de seguridad
    analyze-architecture/SKILL.md      ← Deteccion de drift
    write-tests/SKILL.md              ← Estrategia de tests
    summarize-context/SKILL.md        ← Compresion de contexto
    archive-state/SKILL.md            ← Ciclo de vida del estado
    sync-schema/SKILL.md              ← Sincronizacion de schema
  memory/                              ← Estado persistente
    architecture.md                    ← Diseno del sistema (fuente de verdad)
    schema.md                         ← Modelo de datos (auto-sincronizado)
    project-state.md                   ← Tareas activas + progreso
    research.md                        ← Log de investigacion
    decisions/                         ← Registros de decisiones arquitectonicas
    archive/                           ← Estados completados
```

---

## Inicio Rapido

### 1. Copiar a tu proyecto

```bash
cp -r antigravity/.agent /ruta/a/tu/proyecto/.agent
cp antigravity/GEMINI.md /ruta/a/tu/proyecto/GEMINI.md
```

### 2. Dejar que el agente configure tu proyecto

```
Configura el directorio .agent/ de este proyecto.
Es un [describe tu proyecto — ej: "SaaS multi-tenant para gestion de restaurantes"].

Stack: [ej: "Next.js 14 + Supabase + Prisma, corriendo en Docker"]
Entidades: [ej: "organizaciones, usuarios, restaurantes, menus, pedidos"]
Multi-tenant: [si/no — ej: "si, RLS con columna org_id"]

Invariantes clave:
- [ej: "Todas las queries deben filtrar por org_id"]
- [ej: "Totales de pedidos recalculados en el servidor"]

Lee rules/project.md, rules/stack.md y memory/architecture.md, y llenalos.
```

### 3. Empezar a construir

```
/feature Agregar registro de usuarios con verificacion por email
/feature #42
/research Comparar Redis vs Memcached
/audit src/auth
/sync-schema
```

---

## Que Personalizar

| Archivo | Que cambiar | Cuando |
|---------|------------|--------|
| `rules/project.md` | Dominio, invariantes, flujos criticos | Setup |
| `rules/stack.md` | Comandos de runtime, paths, config de schema | Setup |
| `memory/architecture.md` | Diseno del sistema, roles, patrones | Setup + evoluciona |

---

## Diferencias con la Version de Claude Code

| Aspecto | Claude Code | Antigravity |
|---------|------------|-------------|
| Directorio config | `.claude/` | `.agent/` |
| Entry point | `CLAUDE.md` | `GEMINI.md` |
| Config de proyecto | `project.yml` (YAML) | `rules/project.md` (Markdown) |
| Config de stack | `stack.yml` (YAML) | `rules/stack.md` (Markdown) |
| Ruteo de modelos | `models.yml` | No necesario (automatico) |
| Definicion de agentes | `agents/*.md` | No necesario (Agent Manager) |
| Pipelines de usuario | `skills/*/SKILL.md` | `workflows/*.md` |
| Capacidades auto | `skills/*/SKILL.md` | `skills/*/SKILL.md` |
