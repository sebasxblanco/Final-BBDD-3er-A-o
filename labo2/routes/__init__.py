# Blueprints: auth (SQLite login) + main, vendors, parts (PostgreSQL).

from routes.auth import auth_bp
from routes.main import main_bp
from routes.parts import parts_bp
from routes.vendors import vendors_bp

__all__ = ["auth_bp", "main_bp", "parts_bp", "vendors_bp"]
