# True Love Scan — arquitectura

## 1. Propósito

True Love Scan es una red pública de participación computacional para convertir una búsqueda imposible en una obra visible, verificable y acumulativa.

El sistema debe registrar esfuerzo de búsqueda y pruebas de trabajo, no custodiar ni solicitar claves privadas. La participación puede ser anónima; la identidad humana es opcional.

## 2. Arquitectura MVP

```text
Web / Desktop / Mobile workers
              |
              v
       Cloudflare Tunnel
              |
              v
      Raspberry Pi coordinator
       API + queue + validator
              |
              v
       SQLite + public snapshots
              |
              v
        True Love Scan UI
```

Firebase queda limitado inicialmente a:

- Hosting del landing y de la interfaz pública.
- Backups opcionales de estadísticas.
- Distribución de assets estáticos.

La Raspberry Pi coordina los jobs, recibe pruebas, mantiene la sesión de los nodos y sirve las estadísticas públicas.

## 3. Componentes

### Worker client

Puede ejecutarse en navegador, desktop, móvil (mientras está abierto) o Raspberry Pi. Sus responsabilidades son:

- Solicitar un job.
- Ejecutar la versión aprobada del algoritmo.
- Enviar heartbeats.
- Enviar pruebas verificables.
- Pausar por batería, temperatura o decisión del usuario.
- Mostrar contribución y estado de la sesión.

El cliente no debe enviar claves privadas, frases semilla ni secretos.

### Coordinator

Servicio Node.js o Python en la Raspberry Pi:

- Crea y asigna jobs.
- Evita jobs duplicados.
- Controla versiones del algoritmo.
- Recibe y valida pruebas.
- Mantiene sesiones y heartbeats.
- Calcula puntos y estadísticas.
- Publica snapshots para el frontend.

### Validator

Valida que cada prueba:

- Pertenezca a un job existente.
- Use la versión correcta.
- No haya sido enviada previamente.
- Produzca un resultado reproducible.
- Respete los límites del protocolo.

La red verifica trabajo matemático; no verifica la identidad física de una persona.

### Public Scan UI

Debe mostrar:

- Nodos online.
- Ciudades aproximadas, solo si el usuario lo permite.
- Tiempo de participación verificada.
- Unidades de trabajo aceptadas.
- Jobs y pruebas recientes.
- Algoritmo activo.
- Estado de los 31 targets.
- Historial diario de la búsqueda.

## 4. Flujo de un job

```text
1. Worker solicita trabajo
2. Coordinator crea o asigna job
3. Worker ejecuta el algoritmo
4. Worker envía heartbeat
5. Worker envía proof
6. Validator recalcula una muestra
7. Job queda accepted o rejected
8. Se actualizan puntos y estadísticas
9. Se publica un snapshot público
```

Ejemplo de job:

```json
{
  "jobId": "scan-000482",
  "algorithm": "truelove-v0.1.0",
  "targetId": 17,
  "challenge": "public-unpredictable-challenge",
  "status": "assigned",
  "expiresAt": "2026-08-23T19:00:00Z"
}
```

Ejemplo de prueba:

```json
{
  "jobId": "scan-000482",
  "nodeId": "anonymous-node-042",
  "operations": 18440221,
  "resultDigest": "0xabc...",
  "counter": 192,
  "submittedAt": "2026-08-23T18:22:00Z"
}
```

## 5. Heartbeat y tiempo verificado

Un heartbeat solo demuestra que el nodo está conectado. La contribución válida combina:

- Heartbeats periódicos.
- Jobs aceptados.
- Contadores que avanzan.
- Pruebas que no se repiten.
- Desafíos nuevos emitidos por el coordinator.

La métrica pública debe llamarse `verified participation`, no simplemente `time online`.

```text
NODE: brooklyn-042
SESSION: 02h 41m
HEARTBEATS: 192
PROOFS ACCEPTED: 192
PROOFS REJECTED: 0
VERIFIED WORK: 18.4M units
```

## 6. Datos y retención

SQLite es suficiente para el MVP si se usa en modo WAL y con backups.

### Datos permanentes

- Targets y metadata de las 31 obras.
- Versiones del algoritmo.
- Estadísticas diarias agregadas.
- Resumen de contribución por nodo.
- Historial de releases.

### Datos temporales

- Heartbeats detallados: 7–30 días.
- Jobs completos: retención limitada.
- Logs técnicos: rotación por tamaño y antigüedad.

No se guardará cada heartbeat para siempre. El sistema conservará agregados, no una base infinita de eventos.

## 7. API inicial

```text
GET  /api/status
GET  /api/stats
GET  /api/targets
GET  /api/nodes
POST /api/session/start
POST /api/heartbeat
POST /api/job/claim
POST /api/proof
POST /api/session/stop
```

Endpoints administrativos:

```text
GET  /api/admin/health
POST /api/admin/algorithm
POST /api/admin/rebuild-snapshot
```

Los endpoints administrativos deben ser locales, estar detrás de VPN o protegerse con Cloudflare Access. No deben quedar públicos.

## 8. Red y seguridad

```text
Worker → scan.truelove.art → Cloudflare → Tunnel → Raspberry Pi
```

La Raspberry no debe tener puertos abiertos directamente hacia Internet.

Medidas mínimas:

- Cloudflare Tunnel.
- HTTPS.
- Rate limiting por sesión y por IP.
- Jobs con expiración.
- Rechazo de pruebas duplicadas.
- Límites de payload.
- Backups automáticos de SQLite.
- Logs rotativos.
- Endpoint administrativo privado.
- Consentimiento explícito antes de usar CPU o batería.

Una clave pública puede usarse opcionalmente para mantener la reputación de un nodo, pero no es necesaria para demostrar cada prueba de trabajo.

## 9. Escalabilidad y migración a Radxa

La aplicación debe ser independiente del hardware. La Raspberry Pi 3 será el primer coordinator; Radxa será una migración de infraestructura, no un cambio de protocolo.

Variables de configuración:

```text
DATABASE_PATH
API_PORT
PUBLIC_URL
WORKER_TIMEOUT
HEARTBEAT_INTERVAL
RETENTION_DAYS
ALGORITHM_VERSION
```

Migración:

```text
1. Detener asignación de jobs
2. Cerrar SQLite correctamente
3. Crear backup y verificar integridad
4. Instalar los mismos servicios en Radxa
5. Restaurar base de datos
6. Cambiar DNS o Tunnel
7. Reanudar jobs
```

Los workers solo deben conocer la API, no el hardware que la ejecuta.

## 10. Fases de implementación

### Fase 0 — simulación

- Datos falsos de nodos.
- Jobs simulados.
- Public Scan visual.
- Sin cómputo real.

### Fase 1 — coordinator local

- API en Raspberry Pi.
- SQLite.
- Worker local.
- Heartbeats.
- Proof validation.
- Dashboard local.

### Fase 2 — red privada

- Varios workers autorizados.
- Cloudflare Tunnel.
- Backups.
- Retención de datos.
- Versionado del algoritmo.

### Fase 3 — red pública

- Cliente web.
- Desktop worker.
- Límites de uso.
- Puntos de participación.
- Leaderboard y archivo histórico.

### Fase 4 — migración

- Radxa o hardware superior.
- Mayor número de workers.
- Cola persistente.
- Base de datos externa si el volumen lo exige.

## 11. Principio del sistema

> Every device searches alone.  
> The network remembers together.

True Love no necesita prometer que encontrará el tesoro. Necesita demostrar, de forma abierta y verificable, cuánto esfuerzo puede organizar una comunidad alrededor de una búsqueda imposible.
