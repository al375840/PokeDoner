import os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

def log_turno(turno, imagen, decision):
    imagen.save(f"logs/turno_{turno:03}.png")
    with open(f"logs/turno_{turno:03}.txt", "w", encoding="utf-8") as f:
        f.write(decision)
