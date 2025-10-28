#!/usr/bin/env python3
"""
Script de démarrage pour le serveur toasty
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from server import serve

if __name__ == '__main__':
    print("Demarrage du serveur toasty...")
    serve()