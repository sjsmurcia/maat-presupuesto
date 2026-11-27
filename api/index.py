"""Entrada de Vercel: la función de Python carga la API, que vive en backend/ (ADR-1)."""

from backend.app import app

__all__ = ["app"]
