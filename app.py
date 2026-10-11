"""Entrada da aplicação Flask para o Vercel."""

from Backend.server import create_app

app = create_app()
