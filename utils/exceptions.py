"""
Excepciones personalizadas para el Proyecto Phoenix.
"""


class PhoenixError(Exception):
    """Excepción base para errores del Proyecto Phoenix."""
    pass


class ExchangeConnectionError(PhoenixError):
    """Error de conexión con el exchange."""
    pass


class DataValidationError(PhoenixError):
    """Error de validación de datos."""
    pass


class RateLimitError(PhoenixError):
    """Error de límite de velocidad del exchange."""
    pass


class InsufficientDataError(PhoenixError):
    """Error por datos insuficientes para análisis."""
    pass


class ConfigurationError(PhoenixError):
    """Error de configuración del sistema."""
    pass


class AnalysisError(PhoenixError):
    """Error durante el análisis técnico o de señales."""
    pass


class SignalDetectionError(PhoenixError):
    """Error específico durante la detección de señales de trading."""
    pass
