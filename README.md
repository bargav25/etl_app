# ETL App Project

## Overview

This project is designed to facilitate ETL (Extract, Transform, Load) processes using Docker and PostgreSQL. It comprises two PostgreSQL databases (`db-initial` and `db-transformed`) and a data processing service that depends on these databases.

## Prerequisites

- Docker and Docker Compose installed on your system.

## Configuration

The `docker-compose.yml` file contains the service definitions for the project, including:

- **data-processing**: A custom service for processing data, which depends on the PostgreSQL databases. It uses volumes to persist data.
- **db-initial**: A PostgreSQL 12 database service for initial data storage. It is configured with custom credentials.
- **db-transformed**: Another PostgreSQL 12 database service for transformed data. It is similarly configured with custom credentials and exposes port 5432 for external access.

Both databases are connected through an internal network for secure communication between services.

## Getting Started

1. Clone this repository to your local machine.
2. Navigate to the project directory.
3. Run `docker-compose up --build` to build and start the containers.
4. Once the containers are running, the `data-processing` service will be able to interact with both PostgreSQL databases as defined.

## Customization

You can customize the PostgreSQL credentials and the shared volume paths in the `docker-compose.yml` file according to your needs. Ensure to update the environment variables and volume paths accordingly.

## Ports

- The `db-transformed` service exposes port 5432 on the host machine, allowing external applications to connect to the transformed database.

## Volumes

- Persistent volumes are used for both databases to ensure data is not lost when the containers are stopped or removed.

## Networks

- An internal network (`internal`) is created to facilitate secure communication between services.

For more detailed instructions on how to interact with the databases or extend this setup, please refer to the official Docker and PostgreSQL documentation.
