#!/bin/bash

# Lab Setup Script for AI Security Course
# This script configures the Linux environment and Docker containers for AI Security tools

set -e

echo "=========================================="
echo "AI Security Course - Lab Environment Setup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed. Please log out and log back in for group changes to take effect."
    exit 0
else
    echo "✅ Docker is already installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose is already installed"
fi

# Create Docker network for AI Security labs
echo ""
echo "Creating Docker network for AI Security labs..."
docker network create ai-security-lab 2>/dev/null || echo "Network already exists"

# Pull base images
echo ""
echo "Pulling required Docker images..."
docker pull python:3.11-slim
docker pull tensorflow/tensorflow:latest
docker pull jupyter/scipy-notebook:latest

# Create lab directories
echo ""
echo "Creating lab directories..."
mkdir -p ../labs/{data,models,notebooks,scripts}
mkdir -p ../labs/data/{raw,processed}
mkdir -p ../labs/models/{checkpoints,deployed}

# Create docker-compose.yml for lab environment
cat > ../docker-compose.yml << 'EOF'
version: '3.8'

services:
  jupyter:
    image: jupyter/scipy-notebook:latest
    container_name: ai-security-jupyter
    ports:
      - "8888:8888"
    volumes:
      - ../labs:/home/jovyan/work
      - ./notebooks:/home/jovyan/notebooks
    networks:
      - ai-security-lab
    environment:
      - JUPYTER_ENABLE_LAB=yes

  tensorflow:
    image: tensorflow/tensorflow:latest
    container_name: ai-security-tensorflow
    volumes:
      - ../labs:/workspace
    networks:
      - ai-security-lab
    command: tail -f /dev/null

networks:
  ai-security-lab:
    external: true
EOF

echo ""
echo "✅ Lab environment setup complete!"
echo ""
echo "To start the lab environment, run:"
echo "  docker-compose up -d"
echo ""
echo "To access Jupyter Lab, open:"
echo "  http://localhost:8888"
echo ""
echo "Default token: Check docker logs with 'docker-compose logs jupyter'"
echo ""

