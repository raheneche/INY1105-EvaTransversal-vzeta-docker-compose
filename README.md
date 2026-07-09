# VZeta — Despliegue de aplicación web contenerizada (Docker + Docker Compose)

**Estudiante:** [TU NOMBRE COMPLETO AQUÍ]
**Asignatura:** INY1105 — Infraestructura de Aplicaciones I
**Evaluación:** Examen Transversal — Entrega de encargo

---

## 1. Justificación técnica

### 1.1 Contenedores vs. hipervisores (virtualización tradicional)

[Completa aquí tu redacción. Ideas guía — desarróllalas con tus palabras:]

- Instalación y licenciamiento: un hipervisor requiere instalar y licenciar un
  sistema operativo completo por cada máquina virtual (y a veces licenciar el
  propio hipervisor), mientras que los contenedores comparten el kernel del
  host y no requieren licencia de SO por instancia.
- Peso y velocidad: las VMs pesan GBs y tardan minutos en levantar; los
  contenedores pesan MBs y levantan en segundos.
- Por qué Docker y no Kubernetes/EKS/AKS/GKE en este caso: la infraestructura
  de VZeta no permite orquestación avanzada; con 3 servicios sobre un único
  host, Docker Compose resuelve la orquestación sin la complejidad operativa
  de un clúster de Kubernetes.

### 1.2 Propuesta de nube pública, privada e híbrida

[Completa aquí. Ideas guía:]

- Nube pública (AWS): usada en este proyecto por costo y elasticidad.
- Nube privada: recomendable si existieran datos sensibles o requisitos
  normativos que exijan control total del hardware.
- Nube híbrida: escenario mixto (carga base on-premise + picos de demanda en
  la nube pública), posible gracias a que la imagen Docker es idéntica en
  cualquier entorno con Docker Engine.

---

## 2. Arquitectura de la solución

```
Cliente ── HTTP:80 ──▶ [ mynginx_container ] ──▶ [ myapp_container ] ──▶ [ db_container ]
           (nginx reverse proxy)      (Flask · imagen propia)      (PostgreSQL + volumen)

Los tres servicios comparten una red Docker (bridge) y se orquestan con
docker-compose sobre una instancia EC2 con Docker Engine (AWS Learner Lab).
```

- **mynginx_container**: NGINX como reverse proxy, único punto de entrada
  público (puerto 80), redirige el tráfico hacia `myapp_container`.
- **myapp_container**: aplicación Flask (imagen propia construida con
  `Dockerfile`, base `python:3-slim`). Se conecta a PostgreSQL, registra la
  visita y muestra el contador acumulado.
- **db_container**: PostgreSQL (imagen oficial) con volumen para persistencia
  de datos.

---

## 3. Estructura del repositorio

```
repo/
├── app/
│   ├── app.py              # Lógica Flask: conecta a Postgres y cuenta visitas
│   └── requirements.txt    # flask, psycopg2-binary
├── Dockerfile               # Construye la imagen de myapp_container
├── nginx/
│   └── default.conf         # Configuración del reverse proxy
├── docker-compose.yml       # Orquesta nginx + myapp + db, red y volumen
├── evidencias/               # Capturas de pantalla del despliegue
└── README.md
```

---

## 4. Procedimiento de despliegue paso a paso

### 4.1 Instancia EC2 (AWS Learner Lab)

- Región: `us-east-1`, tipo `t2.small`/`t3.small`, key pair `vockey`.
- Security Group con puerto **80** (HTTP) y **22** (SSH) abiertos.

![Instancia EC2 en ejecución](evidencias/01-ec2-running.png)
*Instancia EC2 corriendo con IP pública asignada y Security Group con puerto 80 abierto.*

### 4.2 Instalación de Docker Engine y Docker Compose

```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
# plugin docker compose...
docker --version
docker compose version
```

![Docker instalado](evidencias/02-docker-instalado.png)
*Verificación de versión de Docker y Docker Compose ya instalados en la instancia.*

### 4.3 Clonar el repositorio y construir la imagen propia

```bash
git clone https://github.com/<tu_usuario>/<tu_repo>.git
cd <tu_repo>
docker build -t myapp:latest .
docker images
```

![Imagen construida](evidencias/03-docker-build.png)
*Construcción de la imagen propia de myapp_container (FROM python:3-slim).*

### 4.4 Levantar el stack completo

```bash
docker compose up -d
docker compose ps
```

![Stack levantado](evidencias/04-compose-ps.png)
*Los tres contenedores (nginx, app, db) en estado "Up" tras `docker compose up -d`.*

### 4.5 Volumen y persistencia

```bash
docker inspect db_container --format '{{json .Mounts}}'
```

![Inspect Mounts](evidencias/05-inspect-mounts.png)
*Sección Mounts del contenedor de la base de datos, mostrando el volumen persistente.*

Prueba de persistencia:
```bash
docker compose down
docker compose up -d
```
El contador de visitas se mantuvo tras bajar y volver a levantar el stack.

### 4.6 Otras operaciones de inspect

```bash
docker network inspect vzeta_net
docker inspect mynginx_container
```

![Inspect red](evidencias/06-inspect-network.png)
*Inspección de la red Docker creada por docker-compose.*

### 4.7 Comprobación de funcionamiento

```bash
curl http://<IP_PUBLICA_EC2>/
```

![App funcionando](evidencias/07-app-funcionando.png)
*Aplicación mostrando el contador de visitas desde el navegador.*

![Curl funcionando](evidencias/08-curl.png)
*Respuesta exitosa vía curl contra la IP pública de la instancia.*

### 4.8 Ciclo de vida de contenedores

```bash
docker logs myapp_container
docker stats --no-stream
docker restart myapp_container
docker stop mynginx_container
docker rename mynginx_container mynginx_container_old && docker rename mynginx_container_old mynginx_container
docker rm <contenedor_detenido>
docker rmi <imagen_de_prueba>
docker compose up -d   # se deja el stack operativo nuevamente
```

![Ciclo de vida](evidencias/09-lifecycle.png)
*Evidencia de logs, stats, restart, stop, rename y remove de contenedores/imágenes.*

---

## 5. Conclusión

[Cierra con 2-3 líneas: el stack cumple lo solicitado, corre en AWS Learner
Lab con Docker Compose, la persistencia funciona y Docker fue la elección
correcta dado que no se permite orquestación avanzada.]
