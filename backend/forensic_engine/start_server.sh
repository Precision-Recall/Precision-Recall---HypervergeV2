#!/bin/bash

echo "============================================================"
echo "Forensic Accountability & Anomaly Detector"
echo "============================================================"
echo ""

# Check Qdrant
echo "Checking Qdrant connection..."
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "✓ Qdrant is running on port 6333"
else
    echo "✗ Qdrant is not running"
    echo "Starting Qdrant..."
    docker run -d -p 6333:6333 --name qdrant qdrant/qdrant 2>/dev/null || \
        docker start qdrant 2>/dev/null
    echo "Waiting for Qdrant..."
    sleep 3
fi

echo ""
echo "Starting Forensic WebSocket Server on port 6060..."
echo "Endpoint: ws://localhost:6060/chat"
echo ""

python websocket_server.py
