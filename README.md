# Microservices Architecture

This repository contains a microservices architecture simulation for an autonomous system, composed of several Docker containers that communicate through RabbitMQ.

## Microservices Architecture

- **dummy-computer-vision**: Simulates computer vision, sending data (cone matrices) via RabbitMQ.
- **dummy-slam**: Receives data from computer vision, processes it, and produces odometry data and cone positions.
- **dummy-path-planning**: Receives cone positions, calculates waypoints through triangulation and interpolation, and sends them to the control microservice.
- **dummy-high-level-control**: Receives odometry data and waypoints, calculates steering and acceleration commands, and publishes them to a dedicated queue.
- **message-broker**: RabbitMQ (with management interface) for communication between microservices.

## System Launch

To start the entire system, run:

```sh
bash launch_system.sh
```

This script:
1. Builds all necessary Docker images via `build-docker-images.sh`.
2. Starts all containers via `docker-compose`.
3. Stops containers when finished.

> **Note:** On macOS, `sudo` is not required for Docker commands.

## Requirements

- Docker and Docker Compose installed.
- Python 3.9 (used as base for all containers).

## Inter-microservice Communication

Communication occurs through RabbitMQ queues, with the following main flows:

- `computer_vision` → `slam`
- `slam-cones` → `path-planning`
- `slam-odometry` → `high-level-control`
- `path_planning` → `high-level-control`
- `hlc_output` → (final system output)

All microservices use the Python `pika` library to interface with RabbitMQ, through the custom API [`dummy_dvde_api.py`](dummy_dvde_api.py).

## Docker Image Building

Each microservice has a `build_image.sh` script that:
- Copies the `dummy_dvde_api.py` library to a temporary folder.
- Builds the Docker image with a specific name (`as-<service-name>`).

Python dependencies are installed in their respective Dockerfiles (e.g., `numpy`, `scipy`, `triangle`, `pika`).

## RabbitMQ Configuration

RabbitMQ is started as a Docker service with:
- User: `admin`
- Password: `admin`
- AMQP Port: `5672`
- Management Port: `15672` (accessible via browser for monitoring)

## Useful References

- [docker-compose.yml](docker-compose.yml): defines all services and the virtual network.
- [dummy_dvde_api.py](dummy_dvde_api.py): API for RabbitMQ communication.
- Each microservice has its own folder with `Dockerfile`, `build_image.sh`, and source code in `src/`.

## Getting Started

1. Clone this repository
2. Ensure Docker and Docker Compose are installed
3. Run `bash launch_system.sh` to start the system
4. Access RabbitMQ management interface at `http://localhost:15672` (admin/admin)
5. Monitor the message flows between microservices

## Architecture Overview

```
Computer Vision → SLAM → Path Planning → High Level Control
                    ↓
                Odometry
                    ↓
            High Level Control
```

The system simulates a typical autonomous vehicle pipeline where:
1. Computer vision detects cones in the environment
2. SLAM processes this data to determine vehicle position and map cone locations
3. Path planning calculates optimal waypoints based on cone positions
4. High-level control generates steering and acceleration commands

---

**Note:** This system is an educational simulation and does not represent a production-ready solution for real vehicles. The generated data is fictitious and serves only to test the communication pipeline between microservices.