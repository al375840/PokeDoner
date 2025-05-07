class MemoriaContexto:
    def __init__(self, max_turnos=5):
        self.turnos = []
        self.max_turnos = max_turnos

    def actualizar(self, entrada: str):
        self.turnos.append(entrada)
        if len(self.turnos) > self.max_turnos:
            self.turnos.pop(0)

    def obtener(self):
        return "\n".join(self.turnos)
