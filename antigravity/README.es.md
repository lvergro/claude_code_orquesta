# Orquesta para Antigravity

Framework de orquestacion multi-agente adaptado para [Google Antigravity](https://antigravity.google) — el IDE agentico de Google basado en VS Code.

## Que es esto?

Orquesta proporciona workflows estructurados, memoria persistente y patrones de coordinacion para desarrollo agentico. Esta version esta adaptada del original para Claude Code para funcionar con las convenciones nativas del directorio `.agent/` de Antigravity.

## Inicio Rapido

1. **Copiar a tu proyecto:**
   ```bash
   cp -r antigravity/.agent /ruta/a/tu/proyecto/.agent
   cp antigravity/GEMINI.md /ruta/a/tu/proyecto/GEMINI.md
   ```

2. **Configurar la identidad del proyecto:**
   Editar `.agent/rules/project.md` — nombre del proyecto, entidades de dominio, invariantes.

3. **Configurar el stack:**
   Editar `.agent/rules/stack.md` — comandos de runtime (test, lint, build, dev).

4. **Documentar la arquitectura:**
   Editar `.agent/memory/architecture.md` — describir el diseno del sistema.

5. **Empezar a trabajar:**
   - `/feature` — Entrega de feature completa (issue → PR)
   - `/develop` — Pipeline maestro para cambios complejos
   - `/quick` — Camino rapido para fixes triviales
   - `/research` — Investigacion tecnica
   - `/audit` — Auditoria de seguridad
   - `/sync-schema` — Sincronizar modelo de datos desde archivos fuente
   - `/prepare-commit` — Validar y commitear

## Estructura

```
GEMINI.md                              ← Instrucciones top-level (siempre cargadas)
.agent/
  rules/                               ← Siempre cargadas en contexto
    project.md                         ← Identidad del proyecto, dominio, invariantes
    stack.md                           ← Comandos de runtime y paths
    conventions.md                     ← Estandares de codigo y git
  workflows/                           ← Invocados por el usuario con /
    feature.md                         ← /feature (issue → PR)
    develop.md                         ← /develop (pipeline E2E)
    quick.md                           ← /quick (camino rapido)
    research.md                        ← /research
    audit.md                           ← /audit
    prepare-commit.md                  ← /prepare-commit
  skills/                              ← Auto-activados por el agente
    validate-invariants/SKILL.md       ← Chequeos de seguridad
    analyze-architecture/SKILL.md      ← Deteccion de drift
    write-tests/SKILL.md              ← Estrategia de tests
    summarize-context/SKILL.md        ← Compresion de contexto
    archive-state/SKILL.md            ← Ciclo de vida del estado
    sync-schema/SKILL.md              ← Sincronizacion de schema (auto + manual)
    parallel/SKILL.md                 ← Coordinacion multi-sesion
  memory/                              ← Estado persistente (directorio custom)
    architecture.md                    ← Diseno del sistema (fuente de verdad)
    project-state.md                   ← Estado en runtime
    research.md                        ← Log de investigacion
    locks.md                           ← Locks multi-sesion
    decisions/                         ← Registros de Decisiones Arquitectonicas
    archive/                           ← Archivos de estado completados
```

## Que Personalizar

| Archivo | Que cambiar |
|---------|------------|
| `GEMINI.md` | Generalmente no necesita cambios |
| `rules/project.md` | Nombre del proyecto, entidades, invariantes, flujos criticos |
| `rules/stack.md` | Comandos de runtime, paths, metadata del framework |
| `rules/conventions.md` | Estilo de codigo, patrones de test (si difieren de los defaults) |
| `memory/architecture.md` | La arquitectura real de tu sistema |

## Diferencias con la Version de Claude Code

| Aspecto | Claude Code (orquesta) | Antigravity |
|---------|----------------------|-------------|
| Directorio config | `.claude/` | `.agent/` |
| Top-level | `CLAUDE.md` | `GEMINI.md` |
| Config de proyecto | `project.yml` (YAML) | `rules/project.md` (Markdown) |
| Config de stack | `stack.yml` (YAML) | `rules/stack.md` (Markdown) |
| Ruteo de modelos | `models.yml` | No necesario (automatico) |
| Definicion de agentes | `agents/*.md` | No necesario (Agent Manager) |
| Pipelines de usuario | `skills/*/SKILL.md` (user-invocable) | `workflows/*.md` |
| Capacidades auto | `skills/*/SKILL.md` (auto) | `skills/*/SKILL.md` |

## Como Funciona Dentro de Antigravity

Al abrir tu proyecto en Antigravity, todo se carga automaticamente:

| Tipo | Como lo maneja Antigravity |
|------|---------------------------|
| `GEMINI.md` | Se inyecta en cada prompt (como instrucciones de sistema) |
| `.agent/rules/*.md` | Siempre cargados en contexto — el agente los ve en cada interaccion |
| `.agent/workflows/*.md` | Aparecen al escribir `/` en el chat — pipelines invocados por el usuario |
| `.agent/skills/*/SKILL.md` | Auto-activados — el agente los carga cuando son semanticamente relevantes a la tarea |
| `.agent/memory/` | Directorio custom — no es nativo de Antigravity, pero las rules lo referencian asi que el agente lee/escribe ahi |

### Usando Workflows

Escribe `/` en el chat de Antigravity para ver los workflows disponibles:

```
/feature agregar dashboard de estadisticas    → issue → spec → worktree → PR
/develop refactorizar sistema de roles        → plan → ejecutar en loop → commit
/quick fix typo en login page                 → implementar → test → commit
/research comparar date-fns vs dayjs          → investigar → escribir en research.md
/audit src/auth                               → analisis de seguridad → reporte
/prepare-commit                               → validar tests + invariantes → mensaje de commit
```

### Como se Auto-Activan los Skills

No invocas los skills directamente. El agente los activa cuando los necesita:

- Antes de un commit → **validate-invariants** chequea reglas de seguridad
- Durante `/develop` cada 3 tareas → **summarize-context** comprime el estado
- Cuando `/develop` termina → **archive-state** resetea project-state.md
- Cuando abres 2+ terminales con `/parallel` → **parallel** coordina via locks
- Cuando un workflow necesita tests → **write-tests** define la estrategia
- Cuando se chequea la arquitectura → **analyze-architecture** detecta drift

### Sistema de Memoria

La memoria no es nativa de Antigravity — es una convencion forzada por las rules:

- `memory/architecture.md` — se lee antes de cualquier codigo, fuente de verdad del diseno
- `memory/schema.md` — modelo de datos compacto, auto-sincronizado al inicio del pipeline
- `memory/project-state.md` — se actualiza durante el desarrollo, permite resumir entre sesiones
- `memory/research.md` — log de investigacion
- `memory/decisions/DEC-*.md` — registros de decisiones arquitectonicas
- `memory/locks.md` — coordinacion multi-sesion para `/parallel`

El agente lee y actualiza estos archivos como parte de la ejecucion de los workflows.

## Convenciones

- **Rules** se cargan siempre — mantenerlas concisas
- **Workflows** son invocados por el usuario — contienen la logica completa del pipeline
- **Skills** se auto-activan — el agente los carga cuando son semanticamente relevantes
- **Memory** no es una feature nativa de Antigravity — es un directorio custom referenciado por las rules
