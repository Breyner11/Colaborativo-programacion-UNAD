import datetime
import traceback
from abc import ABC, abstractmethod
from typing import List, Dict, Any


# ==================== EXCEPCIONES PERSONALIZADAS ====================

class SoftwareFJError(Exception):
    """Excepción base para el sistema Software FJ"""

    def __init__(self, mensaje: str, codigo: str = "ERROR_GENERAL"):
        self.mensaje = mensaje
        self.codigo = codigo
        self.timestamp = datetime.datetime.now()
        super().__init__(self.mensaje)


class ClienteInvalidoError(SoftwareFJError):
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "CLIENTE_INVALIDO")


class ServicioInvalidoError(SoftwareFJError):
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "SERVICIO_INVALIDO")


class ReservaInvalidaError(SoftwareFJError):
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "RESERVA_INVALIDA")


class OperacionNoPermitidaError(SoftwareFJError):
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "OPERACION_NO_PERMITIDA")


# ==================== LOGGER ====================

class Logger:
    """Gestor de logs simple con archivo"""

    LOG_FILE = "software_fj_logs.txt"

    @staticmethod
    def log_event(evento: str, nivel: str = "INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{timestamp}] [{nivel}] {evento}\n"

        try:
            with open(Logger.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(linea)

        except Exception as e:
            print(f"CRÍTICO: No se puede escribir en log: {e}")

    @staticmethod
    def log_error(error: Exception, contexto: str = ""):

        mensaje_error = f"{contexto} | {str(error)}"

        Logger.log_event(mensaje_error, "ERROR")

        try:
            with open(Logger.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(traceback.format_exc() + "\n")

        except:
            pass


# ==================== CLASE ABSTRACTA BASE ====================

class EntidadSistema(ABC):
    """Clase abstracta base para entidades del sistema"""

    def __init__(self, id_entidad: str):

        if not id_entidad or not isinstance(id_entidad, str):
            raise ValueError("ID de entidad requerido y debe ser string")

        self._id = id_entidad
        self._fecha_creacion = datetime.datetime.now()

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def obtener_info(self) -> Dict[str, Any]:
        pass


# ===================== CLIENTE ====================

class Cliente(EntidadSistema):

    def __init__(self, id_cliente: str, nombre: str, email: str, telefono: str):

        super().__init__(id_cliente)

        self._validar_datos(nombre, email, telefono)

        self._nombre = nombre.strip()
        self._email = email.strip().lower()
        self._telefono = telefono.strip()

        self._reservas_activas: List['Reserva'] = []

    def _validar_datos(self, nombre: str, email: str, telefono: str):

        if not nombre or len(nombre.strip()) < 3:
            raise ClienteInvalidoError(
                "Nombre debe tener al menos 3 caracteres"
            )

        if "@" not in email or "." not in email:
            raise ClienteInvalidoError("Email inválido")

        if not telefono or len(telefono.strip()) < 7:
            raise ClienteInvalidoError("Teléfono inválido")

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def email(self) -> str:
        return self._email

    def agregar_reserva(self, reserva: 'Reserva'):
        self._reservas_activas.append(reserva)

    def obtener_info(self) -> Dict[str, Any]:

        return {
            "id": self.id,
            "nombre": self._nombre,
            "email": self._email,
            "telefono": self._telefono,
            "reservas_activas": len(self._reservas_activas)
        }


# ===================== SERVICIOS ====================

class Servicio(EntidadSistema, ABC):

    def __init__(self, id_servicio: str, nombre: str, precio_base: float):

        super().__init__(id_servicio)

        if precio_base <= 0:
            raise ServicioInvalidoError(
                "Precio base debe ser mayor a 0"
            )

        self._nombre = nombre
        self._precio_base = precio_base

    @abstractmethod
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        pass

    @abstractmethod
    def describir(self) -> str:
        pass

    def obtener_info(self) -> Dict[str, Any]:

        return {
            "id": self.id,
            "nombre": self._nombre,
            "precio_base": self._precio_base
        }


# ===================== RESERVA DE SALA ====================

class ReservaSala(Servicio):

    def __init__(self, id_servicio: str, capacidad: int):

        super().__init__(
            id_servicio,
            "Reserva de Sala",
            50000
        )

        self.capacidad = capacidad

    def calcular_costo(self, duracion: float, **kwargs) -> float:

        if duracion is None or duracion <= 0:
            raise ServicioInvalidoError(
                "La duración debe ser mayor a 0"
            )

        costo = self._precio_base * duracion

        if kwargs.get("proyector", False):
            costo += 15000

        return costo

    def describir(self) -> str:

        return (
            f"Reserva de sala "
            f"(capacidad {self.capacidad} personas) "
            f"- ${self._precio_base}/hora"
        )


# ===================== ALQUILER DE EQUIPO ====================

class AlquilerEquipo(Servicio):

    def __init__(self, id_servicio: str, equipo: str):

        super().__init__(
            id_servicio,
            f"Alquiler {equipo}",
            80000
        )

        self.equipo = equipo

    def calcular_costo(self, duracion: float, **kwargs) -> float:

        if duracion is None:
            raise TypeError("La duración no puede ser nula")

        costo = self._precio_base * duracion

        if kwargs.get("seguro", False):
            costo *= 1.1

        return costo

    def describir(self) -> str:

        return f"Alquiler de {self.equipo} - ${self._precio_base}/hora"


# ===================== ASESORÍA ====================

class AsesoriaEspecializada(Servicio):

    def __init__(self, id_servicio: str, especialista: str):

        super().__init__(
            id_servicio,
            "Asesoría Especializada",
            120000
        )

        self.especialista = especialista

    def calcular_costo(self, duracion: float, **kwargs) -> float:

        if duracion is None:
            raise TypeError("La duración no puede ser nula")

        costo = self._precio_base * duracion

        if kwargs.get("compleja", False):
            costo *= 1.25

        return costo

    def describir(self) -> str:

        return (
            f"Asesoría con {self.especialista} "
            f"- ${self._precio_base}/hora"
        )


# ===================== RESERVA ====================

class Reserva(EntidadSistema):

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float
    ):

        super().__init__(id_reserva)

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion

        self.estado = "PENDIENTE"
        self.costo_total = 0.0

    def procesar_confirmacion(self, **kwargs):

        try:

            if self.duracion <= 0:
                raise ReservaInvalidaError(
                    f"Duración inválida ({self.duracion}h)"
                )

            self.costo_total = self.servicio.calcular_costo(
                self.duracion,
                **kwargs
            )

            self.estado = "CONFIRMADA"

            Logger.log_event(
                f"Reserva {self.id} procesada para "
                f"{self.cliente.nombre}"
            )

        except (
            ReservaInvalidaError,
            ServicioInvalidoError
        ) as e:

            self.estado = "FALLIDA"

            Logger.log_error(e)

            print(f"Error de proceso: {e.mensaje}")

        except Exception as e:

            self.estado = "ERROR_SISTEMA"

            Logger.log_error(e)

            print(f"Error crítico inesperado: {e}")

        else:

            print(
                f"Reserva {self.id} confirmada. "
                f"Total: ${self.costo_total}"
            )

        finally:

            print(
                f"--- Fin de gestión para la reserva {self.id} ---"
            )

    def obtener_info(self) -> Dict[str, Any]:

        return {
            "id": self.id,
            "cliente": self.cliente.nombre,
            "servicio": self.servicio._nombre,
            "estado": self.estado,
            "total": self.costo_total
        }


# ===================== PRUEBAS =====================

print("\n--- CASO 1: Cliente inválido ---")

c1 = Cliente(
    "C-001",
    "Mar Systems",
    "mar@unad.edu.co",
    "3101234567"
)

s1 = AsesoriaEspecializada(
    "ASE-100",
    "Ing. Soporte"
)

try:

    cliente_error = Cliente(
        "C99",
        "Jo",
        "correo_falso",
        "123"
    )

except ClienteInvalidoError as e:

    Logger.log_error(e)

    print(f"Bloqueado: {e.mensaje}")


print("\n--- CASO 2: Reserva inválida ---")

try:

    reserva_negativa = Reserva(
        "R-ERR",
        c1,
        s1,
        -2
    )

    reserva_negativa.procesar_confirmacion()

except Exception as e:

    Logger.log_error(e)

    print(e)


print("\n--- CASO 3: Exceso de capacidad ---")

try:

    sala_pequena = ReservaSala("S-PEQ", 5)

    personas = 20

    if personas > sala_pequena.capacidad:

        raise OperacionNoPermitidaError(
            f"Capacidad excedida. "
            f"Máximo: {sala_pequena.capacidad}"
        )

except OperacionNoPermitidaError as e:

    Logger.log_error(e)

    print(e.mensaje)


print("\n--- CASO 4: Parámetro faltante ---")

try:

    asesoria = AsesoriaEspecializada(
        "ASE-01",
        "Ing. Pérez"
    )

    duracion_olvidada = None

    costo = asesoria.calcular_costo(
        duracion_olvidada
    )

except TypeError as e:

    Logger.log_event(
        f"Error de parámetros: {e}",
        "CRITICO"
    )

    print("Parámetro faltante detectado")


print("\n--- CASO 5: Servicio inexistente ---")

try:

    servicio_fantasma = None

    if servicio_fantasma is None:

        raise OperacionNoPermitidaError(
            "Intento de reserva con servicio inexistente"
        )

except OperacionNoPermitidaError as e:

    Logger.log_error(e)

    print(e.mensaje)

finally:

    print("El sistema sigue estable")


print("\n--- CASO 6: Encadenamiento de excepciones ---")

try:

    try:

        resultado = 100 / 0

    except ZeroDivisionError as e:

        raise SoftwareFJError(
            "Error crítico en cálculos"
        ) from e

except SoftwareFJError as e:

    Logger.log_error(e)

    print(e.mensaje)

    print(f"Causa original: {e.__cause__}")


print("\n--- CASO 7: Fecha inválida ---")

try:

    fecha_reserva = datetime.datetime(2023, 5, 10)

    if fecha_reserva < datetime.datetime.now():

        raise ReservaInvalidaError(
            "No se permiten reservas en fechas pasadas"
        )

except ReservaInvalidaError as e:

    Logger.log_error(e)

    print(e.mensaje)


print("\n--- CASO 8: Equipo fuera de servicio ---")

try:

    laptop = AlquilerEquipo(
        "EQ-001",
        "Laptop Dell XPS"
    )

    disponible = False

    if not disponible:

        raise ServicioInvalidoError(
            f"El equipo {laptop.equipo} "
            f"está en mantenimiento"
        )

except ServicioInvalidoError as e:

    Logger.log_error(e)

    print(e.mensaje)


print("\n--- CASO 9: Reserva exitosa ---")

try:

    cliente_ok = Cliente(
        "C-010",
        "Carlos Ruiz",
        "carlos@gmail.com",
        "3205557788"
    )

    servicio_ok = AsesoriaEspecializada(
        "ASE-55",
        "Dra. Montoya"
    )

    total = servicio_ok.calcular_costo(
        3.5,
        compleja=True
    )

    Logger.log_event(
        f"RESERVA EXITOSA: "
        f"{cliente_ok.nombre}"
    )

    print(f"Factura generada: ${total}")

except Exception as e:

    Logger.log_error(e)

    print(e)


print("\n--- CASO 10: Error de tipo ---")

try:

    duracion_erronea = "dos horas"

    total = servicio_ok.calcular_costo(
        duracion_erronea
    )

except TypeError as e:

    Logger.log_error(e)

    print("Error de tipo detectado")

finally:

    print("\n--- FIN DE LA SIMULACIÓN ---")

    Logger.log_event(
        "Ciclo de pruebas completado con éxito"
    )


# ===================== MAIN =====================

def ejecutar_sistema_fj():

    print("=" * 50)
    print("SISTEMA DE GESTIÓN SOFTWARE FJ")
    print("=" * 50)

    print(
        "\n[INFO] Simulación finalizada. "
        "Revise el archivo de logs."
    )


if __name__ == "__main__":

    ejecutar_sistema_fj()
