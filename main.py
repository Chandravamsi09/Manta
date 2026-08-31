#!/usr/bin/env python3
"""
Manta ML Systems Platform — Primary Application Entry Point
"""
import os
import sys
import uvicorn
from manta.gateway.api import create_app
from manta.core.logging import setup_logging, get_logger

logger = get_logger("main")

def main():
    setup_logging(level="INFO")
    logger.info("Initializing Manta Distributed ML Systems Gateway...")
    app = create_app()
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    logger.info(f"Starting server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()
