"""
Gestor de configuración centralizado para el Proyecto Phoenix.

Maneja la carga segura de variables de entorno y parámetros de configuración
desde archivos .env y config.ini.
"""

import os
import configparser
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from utils.exceptions import ConfigurationError


class ConfigManager:
    """
    Gestor centralizado de configuración del sistema.
    
    Carga y gestiona variables de entorno sensibles desde .env
    y parámetros de configuración desde config.ini.
    """
    
    def __init__(self, config_file: str = "config.ini", env_file: str = ".env"):
        """
        Inicializa el gestor de configuración.
        
        Args:
            config_file: Ruta al archivo de configuración
            env_file: Ruta al archivo de variables de entorno
        """
        self.config_file = config_file
        self.env_file = env_file
        self._config = configparser.ConfigParser()
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """
        Carga la configuración desde archivos .env y config.ini.
        
        Raises:
            ConfigurationError: Si no se pueden cargar los archivos de configuración
        """
        # Cargar variables de entorno
        load_dotenv(self.env_file)
        
        # Cargar archivo de configuración
        if not os.path.exists(self.config_file):
            raise ConfigurationError(f"Archivo de configuración no encontrado: {self.config_file}")
        
        try:
            self._config.read(self.config_file, encoding='utf-8')
        except Exception as e:
            raise ConfigurationError(f"Error leyendo archivo de configuración: {str(e)}")
    
    # Variables de entorno sensibles (desde .env)
    def get_exchange_id(self) -> str:
        """Obtiene el ID del exchange."""
        return self._get_env_var('EXCHANGE_ID', 'binance')
    
    def get_api_key(self) -> Optional[str]:
        """Obtiene la clave API del exchange."""
        return os.getenv('API_KEY')
    
    def get_api_secret(self) -> Optional[str]:
        """Obtiene la clave secreta del exchange."""
        return os.getenv('API_SECRET')
    
    def get_telegram_bot_token(self) -> str:
        """Obtiene el token del bot de Telegram."""
        token = self._get_env_var('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ConfigurationError("TELEGRAM_BOT_TOKEN es requerido")
        return token
    
    def get_telegram_chat_id(self) -> str:
        """Obtiene el ID del chat de Telegram."""
        chat_id = self._get_env_var('TELEGRAM_CHAT_ID')
        if not chat_id:
            raise ConfigurationError("TELEGRAM_CHAT_ID es requerido")
        return chat_id
    
    def get_ai_api_key(self) -> Optional[str]:
        """Obtiene la clave API para el servicio de IA."""
        return os.getenv('AI_API_KEY')
    
    # Parámetros de configuración (desde config.ini)
    def get_trading_pair(self) -> str:
        """Obtiene el par de trading."""
        return self._get_config_value('trading', 'pair', 'BTC/USDC')
    
    def get_timeframe(self) -> str:
        """Obtiene la temporalidad."""
        return self._get_config_value('trading', 'timeframe', '2h')
    
    def get_ema_period(self) -> int:
        """Obtiene el período de la EMA."""
        return self._get_config_int('indicators', 'ema_period', 21)
    
    def get_rsi_period(self) -> int:
        """Obtiene el período del RSI."""
        return self._get_config_int('indicators', 'rsi_period', 14)
    
    def get_macd_fast(self) -> int:
        """Obtiene el período rápido del MACD."""
        return self._get_config_int('indicators', 'macd_fast', 12)
    
    def get_macd_slow(self) -> int:
        """Obtiene el período lento del MACD."""
        return self._get_config_int('indicators', 'macd_slow', 26)
    
    def get_macd_signal(self) -> int:
        """Obtiene el período de señal del MACD."""
        return self._get_config_int('indicators', 'macd_signal', 9)
    
    def get_volume_avg_period(self) -> int:
        """Obtiene el período de la media de volumen."""
        return self._get_config_int('indicators', 'volume_avg_period', 20)
    
    def get_ai_provider(self) -> str:
        """Obtiene el proveedor de IA."""
        return self._get_config_value('ai', 'provider', 'gemini')
    
    def get_data_limit(self) -> int:
        """Obtiene el límite de velas históricas a solicitar."""
        return self._get_config_int('data', 'limit', 200)
    
    def get_log_level(self) -> str:
        """Obtiene el nivel de logging."""
        return self._get_config_value('logging', 'level', 'INFO')
    
    def get_log_file(self) -> str:
        """Obtiene el archivo de log."""
        return self._get_config_value('logging', 'file', 'logs/phoenix.log')
    
    def _get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Obtiene una variable de entorno.
        
        Args:
            key: Nombre de la variable
            default: Valor por defecto
            
        Returns:
            Valor de la variable o default
        """
        return os.getenv(key, default)
    
    def _get_config_value(self, section: str, key: str, default: str = "") -> str:
        """
        Obtiene un valor de configuración.
        
        Args:
            section: Sección del archivo de configuración
            key: Clave de configuración
            default: Valor por defecto
            
        Returns:
            Valor de configuración
        """
        try:
            return self._config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def _get_config_int(self, section: str, key: str, default: int = 0) -> int:
        """
        Obtiene un valor entero de configuración.
        
        Args:
            section: Sección del archivo de configuración
            key: Clave de configuración
            default: Valor por defecto
            
        Returns:
            Valor entero de configuración
        """
        try:
            return self._config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        Obtiene toda la configuración (sin datos sensibles).
        
        Returns:
            Diccionario con toda la configuración
        """
        return {
            'trading': {
                'pair': self.get_trading_pair(),
                'timeframe': self.get_timeframe(),
            },
            'indicators': {
                'ema_period': self.get_ema_period(),
                'rsi_period': self.get_rsi_period(),
                'macd_fast': self.get_macd_fast(),
                'macd_slow': self.get_macd_slow(),
                'macd_signal': self.get_macd_signal(),
                'volume_avg_period': self.get_volume_avg_period(),
            },
            'ai': {
                'provider': self.get_ai_provider(),
            },
            'data': {
                'limit': self.get_data_limit(),
            },
            'logging': {
                'level': self.get_log_level(),
                'file': self.get_log_file(),
            }
        }
