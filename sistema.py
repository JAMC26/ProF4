"""Sistema académico de clientes, servicios y reservas de Software FJ.

Los datos se mantienen en memoria. El archivo de registro guarda eventos,
no almacena los clientes ni permite recuperar reservas al reiniciar.
"""
from abc import ABC, abstractmethod
import logging
import math


class ErrorSistema(Exception):
    """Error controlado de la aplicación."""


class ErrorValidacion(ErrorSistema):
    """Un dato obligatorio o su valor no es válido."""


class ErrorReserva(ErrorSistema):
    """Una operación sobre la reserva no está permitida."""


def numero(valor, nombre, minimo=0):
    """Convierte y valida un número, conservando la causa de conversión."""
    try:
        if isinstance(valor, bool):
            raise ValueError("Un valor lógico no es un número válido")
        resultado = float(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise ErrorValidacion(f"{nombre} debe ser un número válido") from error
    if not math.isfinite(resultado) or resultado < minimo:
        raise ErrorValidacion(f"{nombre} debe ser finito y mayor o igual a {minimo}")
    return resultado


def texto(valor, nombre):
    """Exige texto no vacío para evitar datos personales incompletos."""
    if not isinstance(valor, str) or not valor.strip():
        raise ErrorValidacion(f"{nombre} es obligatorio")
    return valor.strip()


class Entidad(ABC):
    """Contrato común para las entidades que se describen en pantalla."""
    @abstractmethod
    def describir(self):
        """Devuelve una descripción de la entidad."""


class Cliente(Entidad):
    """Protege los datos personales mediante atributos privados y propiedades."""
    def __init__(self, identificacion, nombre, correo):
        self.__identificacion = texto(identificacion, "Identificación")
        self.__nombre = texto(nombre, "Nombre")
        correo = texto(correo, "Correo")
        if correo.count("@") != 1 or any(not parte or ' ' in parte for parte in correo.split('@')):
            raise ErrorValidacion("El correo debe tener usuario y dominio separados por @")
        self.__correo = correo

    @property
    def identificacion(self):
        return self.__identificacion

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    def describir(self):
        return f"Cliente: {self.nombre} (ID {self.identificacion})"


class Servicio(Entidad, ABC):
    """Contrato común para servicios con tarifa por hora y disponibilidad."""
    def __init__(self, nombre, tarifa, disponible=True):
        self._nombre = texto(nombre, "Nombre del servicio")
        self._tarifa = numero(tarifa, "Tarifa", 0.01)
        if not isinstance(disponible, bool):
            raise ErrorValidacion("La disponibilidad debe ser verdadera o falsa")
        self._disponible = disponible

    @property
    def disponible(self):
        return self._disponible

    def validar_parametros(self, duracion):
        """La duración se expresa en horas y debe ser positiva."""
        return numero(duracion, "Duración", 0.01)

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """Variantes mediante parámetros opcionales; porcentajes entre 0 y 100."""
        horas = self.validar_parametros(duracion)
        impuesto = numero(impuesto, "Impuesto")
        descuento = numero(descuento, "Descuento")
        if impuesto > 100 or descuento > 100:
            raise ErrorValidacion("Impuesto y descuento no pueden superar el 100 %")
        total = self._costo_base(horas) * (1 - descuento / 100) * (1 + impuesto / 100)
        if not math.isfinite(total) or total < 0:
            raise ErrorValidacion("El costo calculado no es válido")
        return round(total, 2)

    @abstractmethod
    def _costo_base(self, horas):
        """Cada servicio define su cálculo antes de ajustes."""


class Sala(Servicio):
    """La sala se cobra por hora y requiere capacidad positiva."""
    def __init__(self, nombre, tarifa, capacidad, disponible=True):
        super().__init__(nombre, tarifa, disponible)
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad < 1:
            raise ErrorValidacion("La capacidad debe ser un entero positivo")
        self._capacidad = capacidad

    def _costo_base(self, horas):
        return self._tarifa * horas

    def describir(self):
        return f"Sala {self._nombre}: capacidad {self._capacidad}; tarifa ${self._tarifa:,.2f}/hora"


class Equipo(Servicio):
    """El equipo añade un cargo fijo de mantenimiento por reserva."""
    def __init__(self, nombre, tarifa, mantenimiento, disponible=True):
        super().__init__(nombre, tarifa, disponible)
        self._mantenimiento = numero(mantenimiento, "Mantenimiento")

    def _costo_base(self, horas):
        return self._tarifa * horas + self._mantenimiento

    def describir(self):
        return f"Equipo {self._nombre}: tarifa ${self._tarifa:,.2f}/hora; mantenimiento ${self._mantenimiento:,.2f}"


class Asesoria(Servicio):
    """La asesoría registra la especialidad y se cobra por hora."""
    def __init__(self, nombre, tarifa, especialidad, disponible=True):
        super().__init__(nombre, tarifa, disponible)
        self._especialidad = texto(especialidad, "Especialidad")

    def _costo_base(self, horas):
        return self._tarifa * horas

    def describir(self):
        return f"Asesoría {self._nombre}: {self._especialidad}; tarifa ${self._tarifa:,.2f}/hora"


class Reserva(Entidad):
    """Controla las transiciones pendiente → confirmada → procesada o cancelada."""
    def __init__(self, cliente, servicio, duracion):
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ErrorValidacion("La reserva requiere un cliente y un servicio válidos")
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = servicio.validar_parametros(duracion)
        self._estado = "pendiente"

    @property
    def estado(self):
        return self._estado

    def confirmar(self):
        if self._estado != "pendiente":
            raise ErrorReserva("Solo se puede confirmar una reserva pendiente")
        if not self._servicio.disponible:
            raise ErrorReserva("El servicio no está disponible")
        self._estado = "confirmada"
        return self.describir()

    def cancelar(self):
        if self._estado not in ("pendiente", "confirmada"):
            raise ErrorReserva("Solo se puede cancelar una reserva pendiente o confirmada")
        self._estado = "cancelada"
        return self.describir()

    def procesar(self, impuesto=0, descuento=0):
        if self._estado != "confirmada":
            raise ErrorReserva("Solo se puede procesar una reserva confirmada")
        costo = self._servicio.calcular_costo(self._duracion, impuesto, descuento)
        self._estado = "procesada"
        return f"{self.describir()} | Total: ${costo:,.2f}"

    def describir(self):
        return f"{self._cliente.nombre} | {self._servicio.describir()} | {self._duracion:g} h | {self._estado}"


class Sistema:
    """Guarda objetos en listas; no usa base de datos ni persistencia de datos."""
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise ErrorValidacion("Cliente inválido")
        if any(c.identificacion == cliente.identificacion for c in self.clientes):
            raise ErrorValidacion("La identificación ya está registrada")
        self.clientes.append(cliente)
        return cliente.describir()

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise ErrorValidacion("Servicio inválido")
        self.servicios.append(servicio)
        return servicio.describir()

    def crear_reserva(self, cliente, servicio, duracion):
        if cliente not in self.clientes or servicio not in self.servicios:
            raise ErrorReserva("El cliente y el servicio deben estar registrados")
        reserva = Reserva(cliente, servicio, duracion)
        self.reservas.append(reserva)
        return reserva


def configurar_registro():
    """Registra eventos en el directorio de ejecución; avisa si no puede hacerlo."""
    try:
        logging.basicConfig(filename="eventos.log", level=logging.INFO,
                            format="%(asctime)s | %(levelname)s | %(message)s", encoding="utf-8")
    except OSError as error:
        print(f"Aviso: no se pudo abrir eventos.log: {error}. Se usará la consola.")
        logging.basicConfig(level=logging.INFO)


def ejecutar_operacion(numero_operacion, descripcion, accion):
    """Aísla errores de cada operación para continuar la simulación."""
    print(f"\n{numero_operacion}. {descripcion}")
    try:
        resultado = accion()
    except (ErrorSistema, TypeError) as error:
        logging.exception("Operación %s fallida: %s", numero_operacion, descripcion)
        print(f"Error controlado: {error}")
    except Exception as error:
        # El límite de cada operación registra errores inesperados y permite
        # que la simulación continúe con la siguiente operación.
        logging.exception("Error inesperado en operación %s: %s", numero_operacion, descripcion)
        print(f"Error inesperado: {error}")
    else:
        logging.info("Operación %s completada: %s", numero_operacion, descripcion)
        if resultado is not None:
            print(resultado)
    finally:
        print("Operación finalizada; la simulación continúa.")
