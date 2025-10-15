"""
Script principal del Proyecto Phoenix.

Este script demuestra el uso del conector del exchange implementado
según las especificaciones de la Fase I - 2.1.
"""

import asyncio
import logging

from utils.config_manager import ConfigManager
from utils.logger import setup_logging
from core.exchange_connector import ExchangeConnector
from utils.exceptions import PhoenixError


async def main():
    """
    Función principal que demuestra el conector del exchange.
    """
    try:
        # Inicializar configuración
        config = ConfigManager()
        
        # Configurar logging
        logger = setup_logging(config)
        logger.info("=== PROYECTO PHOENIX - FASE I ===")
        logger.info("Iniciando conector del exchange...")
        
        # Inicializar conector
        connector = ExchangeConnector(config)
        
        # Probar conexión
        if not connector.test_connection():
            logger.error("No se pudo establecer conexión con el exchange")
            return
        
        # Obtener información del exchange
        exchange_info = connector.get_exchange_info()
        logger.info(f"Exchange conectado: {exchange_info}")
        
        # Obtener parámetros de configuración
        symbol = config.get_trading_pair()
        timeframe = config.get_timeframe()
        limit = config.get_data_limit()
        
        logger.info(f"Obteniendo datos OHLCV para {symbol} en {timeframe}")
        
        # Obtener y validar datos OHLCV
        df = connector.fetch_ohlcv_data(symbol, timeframe, limit)
        
        logger.info("=== DATOS OHLCV VALIDADOS ===")
        logger.info(f"Filas obtenidas: {len(df)}")
        logger.info(f"Rango temporal: {df.index[0]} a {df.index[-1]}")
        logger.info(f"Precio actual (último cierre): {df['close'].iloc[-1]:.2f}")
        logger.info(f"Volumen promedio: {df['volume'].mean():.2f}")
        
        # Mostrar muestra de datos
        logger.info("=== PRIMERAS 5 FILAS ===")
        logger.info(f"\n{df.head()}")
        
        logger.info("=== ÚLTIMAS 5 FILAS ===")
        logger.info(f"\n{df.tail()}")
        
        logger.info("=== CONECTOR DEL EXCHANGE - IMPLEMENTACIÓN EXITOSA ===")
        
    except PhoenixError as e:
        logger.error(f"Error del Proyecto Phoenix: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
