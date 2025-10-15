#!/bin/bash
# OBCMS Docker Stop Script

set -euo pipefail

echo "🛑 Stopping OBCMS Docker services..."

# Stop all services
docker compose down

echo "✅ All services stopped."
echo ""
echo "💡 To remove volumes (reset database):"
echo "   docker compose down -v"
echo ""
echo "🧹 To clean up images:"
echo "   docker system prune"