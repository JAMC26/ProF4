"""Simulación secuencial de operaciones válidas y fallidas."""
from sistema import (Asesoria, Cliente, Equipo, Reserva, Sala, Sistema,
                     configurar_registro, ejecutar_operacion)


def main():
    configurar_registro()
    sistema = Sistema()
    cliente = Cliente("1001", "Ana Pérez", "ana@example.com")
    sala = Sala("Reuniones", 30000, 12)
    equipo = Equipo("Proyector", 15000, 5000)
    asesoria = Asesoria("Tecnológica", 50000, "Software")
    no_disponible = Sala("Sala ocupada", 20000, 5, False)
    datos = {}

    def guardar_reserva():
        datos["reserva"] = sistema.crear_reserva(cliente, sala, 2)
        return datos["reserva"].describir()

    def intentar_no_disponible():
        reserva = sistema.crear_reserva(cliente, no_disponible, 1)
        return reserva.confirmar()

    def cancelar_reserva():
        reserva = sistema.crear_reserva(cliente, asesoria, 1)
        reserva.confirmar()
        return reserva.cancelar()

    operaciones = [
        ("Registrar cliente válido", lambda: sistema.registrar_cliente(cliente)),
        ("Rechazar cliente sin nombre", lambda: Cliente("1002", "", "b@example.com")),
        ("Rechazar identificación repetida", lambda: sistema.registrar_cliente(cliente)),
        ("Registrar sala", lambda: sistema.registrar_servicio(sala)),
        ("Registrar equipo", lambda: sistema.registrar_servicio(equipo)),
        ("Registrar asesoría", lambda: sistema.registrar_servicio(asesoria)),
        ("Rechazar tarifa no numérica", lambda: Sala("Inválida", "abc", 10)),
        ("Rechazar parámetro faltante", lambda: Equipo("Equipo", 1000)),
        ("Crear reserva válida", guardar_reserva),
        ("Confirmar reserva", lambda: datos["reserva"].confirmar()),
        ("Procesar con 19 % de impuesto y 10 % de descuento", lambda: datos["reserva"].procesar(19, 10)),
        ("Rechazar cancelación de reserva procesada", lambda: datos["reserva"].cancelar()),
        ("Registrar sala no disponible", lambda: sistema.registrar_servicio(no_disponible)),
        ("Rechazar confirmación de servicio no disponible", intentar_no_disponible),
        ("Rechazar duración cero", lambda: sistema.crear_reserva(cliente, equipo, 0)),
        ("Calcular precio de equipo", lambda: f"Total: ${equipo.calcular_costo(2):,.2f}"),
        ("Calcular precio de asesoría", lambda: f"Total: ${asesoria.calcular_costo(2):,.2f}"),
        ("Rechazar descuento superior al 100 %", lambda: equipo.calcular_costo(1, descuento=110)),
        ("Confirmar y cancelar una reserva", cancelar_reserva),
        ("Confirmar que el programa sigue activo", lambda: f"Clientes: {len(sistema.clientes)}; servicios: {len(sistema.servicios)}; reservas: {len(sistema.reservas)}"),
    ]
    for indice, (descripcion, accion) in enumerate(operaciones, 1):
        ejecutar_operacion(indice, descripcion, accion)


if __name__ == "__main__":
    main()
