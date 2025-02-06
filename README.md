![Build Status](https://img.shields.io/github/actions/workflow/status/MaBoNi/kubernetes-secret-generator/docker-publish.yml?branch=main&style=for-the-badge)
![License](https://img.shields.io/github/license/MaBoNi/kubernetes-secret-generator?style=for-the-badge)
![Repo Size](https://img.shields.io/github/repo-size/MaBoNi/kubernetes-secret-generator?style=for-the-badge)

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-kubernetes--secret--generator-blue?logo=docker&style=for-the-badge)](https://hub.docker.com/r/maboni82/kubernetes-secret-generator) [![Docker Pulls](https://img.shields.io/docker/pulls/maboni82/kubernetes-secret-generator?style=for-the-badge)](https://hub.docker.com/r/maboni82/kubernetes-secret-generator)

# Kubernetes Secret Generator

A lightweight Flask-based web application that converts `.env` files into Kubernetes Secret JSON files. Supports both `=` and `:` key-value formats and provides a downloadable JSON output for easy Kubernetes integration.

## Features
- **Web-based UI** – Easily input `.env` data and generate Kubernetes Secrets.
- **Supports multiple formats** – Works with both `=` and `:` key-value pairs.
- **Dockerized for easy deployment** – Run in a containerized environment.
- **Base64 Encoding** – Secrets are automatically Base64-encoded as required by Kubernetes.

## Getting Started

### Prerequisites
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation
1. **Clone the repository**:
    ```bash
    git clone https://github.com/MaBoNi/kubernetes-secret-generator.git
    cd kubernetes-secret-generator
    ```

2. **Build and run the Docker container**:
    ```bash
    docker-compose up -d
    ```

3. Open the application in your browser:
    ```
    http://localhost:5050
    ```

### Usage
1. **Paste your `.env` content** into the web form.
2. **Specify the secret name and namespace**.
3. **Generate the Kubernetes Secret JSON file**.
4. **Download and apply the secret**:
    ```bash
    kubectl apply -f generated-secret.json
    ```

## Docker Hub Repository
You can pull the Docker image directly from Docker Hub:
```sh
    docker pull maboni82/kubernetes-secret-generator
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

## Repobeats Analytics

![Alt](https://repobeats.axiom.co/api/embed/cf34db7e1241adc71551704d5ad9dead7edf1b08.svg "Repobeats analytics image")
