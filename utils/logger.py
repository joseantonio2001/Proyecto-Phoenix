"""
Configuración del sistema de logging para el Proyecto Phoenix.
"""

import logging
import logging.handlers
import os
from typing import Optional

from utils.config_manager import ConfigManager


def setup_logging(config_manager: ConfigManager) -> logging.Logger:
    """
    Configura el sistema de logging del proyecto.
    
    Args:
        config_manager: Instancia del gestor de configuración
        
    Returns:
        Logger principal configurado
    """
    # Obtener configuración de logging
    log_level = getattr(logging, config_manager.get_log_level().upper(), logging.INFO)
    log_file = config_manager.get_log_file()
    
    # Crear directorio de logs si no existe
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar el logger principal
    logger = logging.getLogger('phoenix')
    logger.setLevel(log_level)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Formato de logging
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Handler para archivo con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
