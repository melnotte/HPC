# Prueba de Concepto (PoC) – Benchmark WordPress con Siege y ApacheBench

## Objetivo
Realizar el despliegue de Wordpress en HA con un LB con HAProxy y una BD sincronizada en 3 nodos.

## Arquitectura Implementada

- **WordPress** en alta disponibilidad con 3 nodos (`webnode1`, `webnode2`, `webnode3`)
- **MariaDB Galera Cluster** con 3 nodos (`dbnode1`, `dbnode2`, `dbnode3`)
- **HAProxy** como balanceador de carga
- Infraestructura completamente contenedorizada con Docker Compose
- +-----------------------------------------------------------------------+
|                        Docker Compose Stack                           |
|                                                                       |
|  +----------------+    +----------------+    +----------------+       |
|  |   dbnode1      |    |   dbnode2      |    |   dbnode3      |       |
|  |  (Galera)      |<-->|  (Galera)      |<-->|  (Galera)      |       |
|  |  Primary Node  |    |  Secondary     |    |  Secondary     |       |
|  +-------+--------+    +-------+--------+    +-------+--------+       |
|          |                     |                     |                |
|          |                     |                     |                |
|  +-------v--------+   +--------v-------+   +--------v-------+         |
|  |   webnode1     |   |   webnode2     |   |   webnode3     |         |
|  |  (WordPress)   |   |  (WordPress)   |   |  (WordPress)   |         |
|  +-------+--------+   +--------+-------+   +--------+-------+         |
|          |                     |                     |                |
|          +----------+----------+----------+----------+                |
|                     |                     |                           |
|              +------v---------------------v------+                    |
|              |            HAProxy               |                     |
|              |  (Load Balancer/Reverse Proxy)   |                     |
|              +----------------+-----------------+                     |
|                               |                                       |
|                       +-------v--------+                              |
|                       |    Host:80     |                              |
|                       |    Host:3306   |                              |
|                       +----------------+                              |
|                                                                       |
+-----------------------------------------------------------------------+

## Herramientas de Prueba de Carga

- **Siege**
- **Apache Benchmark (ab)**

## Parámetros de la Prueba Siege

- **Usuarios simultáneos**: 100
- **Duración**: 5 minutos

---

## Resultados

### Siege

| Métrica                  | Valor     |
|--------------------------|-----------|
| Transacciones            | 18,412    |
| Tiempo transcurrido      | 299.84 s  |
| Transacciones por segundo| 61.41     |
| Tiempo de respuesta promedio | 1.58 s|
| Transacciones fallidas   | 0         |
| Concurrencia promedio    | 97.03     |
| Transferencia total      | 65.16 MB  |
| Transacción más larga    | 33.89 s   |

## Parámetros de la Prueba Apache Benchmark
- **Requests**: 3000
- **Concurrencia**: 100

| Métrica                     | Valor            |
|-----------------------------|------------------|
| Solicitudes completadas     | 3000             |
| Tiempo total de prueba      | 90.55 s          |
| Solicitudes por segundo     | 33.13 req/sec    |
| Tiempo por solicitud (media)| 3018 ms          |
| Transferencia total         | 149.6 MB         |
| Transferencia por segundo   | 1613.11 KB/s     |
| Tiempo máximo de solicitud  | 11.5 s           |
| Solicitudes fallidas        | 0                |

### Gráficos

#### 1. Comparación General Siege vs Apache Benchmark

![Gráfico Comparativo](comparacion_siege_ab.png)

#### 2. Rendimiento Apache Benchmark

![Gráfico Apache Benchmark](grafico_ab_resultados.png)

---

## Comparación de Arquitectura

| Característica                   | Arquitectura Original          | Arquitectura Propuesta            |
|----------------------------------|--------------------------------|-----------------------------------|
| IPs Fijas en Red Docker          | Sí                             | No                                |
| Uso de Variables y Seguridad     | Contraseña vacía en nodos      | Contraseña definida               |
| Volúmenes Persistentes separados | Sí                             | Sí                                |
| Reinicio automático              | No                             | `restart: unless-stopped`         |
| Healthchecks                     | No                             | Para nodos de base de datos       |
| Balanceo de carga                | HAProxy con IP fija            | HAProxy estándar                  |
| Escalabilidad                    | Limitada                       | Más flexible                      |

**Mejoras Realizadas:**

- Se implementaron `healthchecks` para asegurar la disponibilidad antes de levantar servicios dependientes.
- Se utilizó `restart: unless-stopped` para mejorar la resiliencia.
- Uso explícito de variables de entorno para seguridad y configuración.
- La arquitectura se mantiene modular y fácilmente replicable sin necesidad de IPs fijas.

---

## Conclusiones

- **Rendimiento sólido:** La arquitectura respondió bien con 100 usuarios concurrentes durante 5 minutos sin fallas.
- **Resiliencia:** Al implementar healthchecks y reinicios automáticos, se asegura mejor disponibilidad ante fallos.
- **Escalabilidad mejorada:** La arquitectura permite escalar fácilmente nodos WordPress o MariaDB según necesidad.
- **Comparación:** se enfoca en modularidad, mejores prácticas de despliegue y resiliencia.
