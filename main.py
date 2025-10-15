"""
Script principal del Proyecto Phoenix - Fase I.

Demuestra la integración completa del conector del exchange y el motor de análisis técnico
según las especificaciones del punto 2.2 del documento "Proyecto Phoenix".
"""

import asyncio
import logging

from utils.config_manager import ConfigManager
from utils.logger import setup_logging
from core.exchange_connector import ExchangeConnector
from core.analysis_engine import TechnicalAnalysisEngine
from utils.exceptions import PhoenixError


async def main():
    """
    Función principal que demuestra la integración completa de la Fase I.
    """
    try:
        # Inicializar configuración
        config = ConfigManager()
        
        # Configurar logging
        logger = setup_logging(config)
        logger.info("=== PROYECTO PHOENIX - FASE I: NÚCLEO DE ANÁLISIS ===")
        logger.info("Iniciando integración completa: Conector + Motor de Análisis...")
        
        # === PASO 1: CONECTOR DEL EXCHANGE ===
        logger.info("--- PASO 1: INICIALIZANDO CONECTOR DEL EXCHANGE ---")
        connector = ExchangeConnector(config)
        
        # Probar conexión
        if not connector.test_connection():
            logger.error("No se pudo establecer conexión con el exchange")
            return
        
        # Obtener información del exchange
        exchange_info = connector.get_exchange_info()
        logger.info(f"Exchange conectado: {exchange_info['name']} ({exchange_info['id']})")
        
        # Obtener parámetros de configuración
        symbol = config.get_trading_pair()
        timeframe = config.get_timeframe()
        limit = config.get_data_limit()
        
        logger.info(f"Obteniendo datos OHLCV para {symbol} en {timeframe}")
        
        # Obtener y validar datos OHLCV
        ohlcv_df = connector.fetch_ohlcv_data(symbol, timeframe, limit)
        
        logger.info("=== DATOS OHLCV OBTENIDOS ===")
        logger.info(f"Filas obtenidas: {len(ohlcv_df)}")
        logger.info(f"Rango temporal: {ohlcv_df.index[0]} a {ohlcv_df.index[-1]}")
        logger.info(f"Precio actual (último cierre): {ohlcv_df['close'].iloc[-1]:.2f}")
        
        # === PASO 2: MOTOR DE ANÁLISIS TÉCNICO ===
        logger.info("--- PASO 2: INICIALIZANDO MOTOR DE ANÁLISIS TÉCNICO ---")
        analysis_engine = TechnicalAnalysisEngine(config)
        
        # Mostrar configuración del motor
        analysis_config = analysis_engine.get_configuration_summary()
        logger.info(f"Configuración del motor: {analysis_config}")
        
        # Enriquecer DataFrame con indicadores técnicos
        logger.info("Calculando indicadores técnicos...")
        enriched_df = analysis_engine.enrich_dataframe(ohlcv_df)
        
        logger.info("=== DATAFRAME ENRIQUECIDO CON INDICADORES ===")
        logger.info(f"Columnas totales: {len(enriched_df.columns)}")
        logger.info(f"Indicadores añadidos: {analysis_engine._get_indicator_columns()}")
        
        # Obtener resumen de indicadores actuales
        indicators_summary = analysis_engine.get_latest_indicators_summary(enriched_df)
        logger.info("=== VALORES ACTUALES DE INDICADORES ===")
        for key, value in indicators_summary.items():
            if value is not None:
                if isinstance(value, float):
                    logger.info(f"{key}: {value:.4f}")
                else:
                    logger.info(f"{key}: {value}")
            else:
                logger.info(f"{key}: N/A")
        
        # === MOSTRAR PRIMERAS Y ÚLTIMAS 5 FILAS ===
        logger.info("=== PRIMERAS 5 FILAS (DATOS + INDICADORES) ===")
        # Mostrar solo las columnas más relevantes para evitar logs muy largos
        relevant_columns = ['open', 'high', 'low', 'close', 'volume', 'EMA21', 'RSI14', 'MACD', 'MACD_Histogram', 'Volume_Avg20']
        available_columns = [col for col in relevant_columns if col in enriched_df.columns]
        
        logger.info(f"Columnas mostradas: {available_columns}")
        logger.info("\n" + str(enriched_df[available_columns].head()))
        
        logger.info("=== ÚLTIMAS 5 FILAS (DATOS + INDICADORES) ===")
        logger.info("\n" + str(enriched_df[available_columns].tail()))
        
        # === VERIFICAR CALIDAD DE LOS DATOS ===
        logger.info("=== VERIFICACIÓN DE CALIDAD DE INDICADORES ===")
        
        # Contar valores válidos por indicador
        indicator_quality = {}
        for indicator in analysis_engine._get_indicator_columns():
            if indicator in enriched_df.columns:
                total_rows = len(enriched_df)
                valid_values = enriched_df[indicator].notna().sum()
                coverage_pct = (valid_values / total_rows) * 100
                indicator_quality[indicator] = {
                    'valid_values': valid_values,
                    'total_rows': total_rows,
                    'coverage_percent': coverage_pct
                }
                logger.info(f"{indicator}: {valid_values}/{total_rows} valores válidos ({coverage_pct:.1f}%)")
        
        # === VERIFICAR DATOS DE LAS ÚLTIMAS 10 VELAS ===
        logger.info("=== INDICADORES EN LAS ÚLTIMAS 10 VELAS ===")
        recent_data = enriched_df[available_columns].tail(10)
        
        # Verificar si hay algún NaN en las últimas filas
        recent_nulls = recent_data.isnull().sum()
        if recent_nulls.sum() > 0:
            logger.warning("Valores nulos encontrados en datos recientes:")
            for col, null_count in recent_nulls[recent_nulls > 0].items():
                logger.warning(f"  {col}: {null_count} valores nulos")
        else:
            logger.info("✅ Todos los indicadores tienen valores válidos en las últimas 10 velas")
        
        logger.info("=== INTEGRACIÓN FASE I - COMPLETADA EXITOSAMENTE ===")
        logger.info("✅ Conector del Exchange: OPERATIVO")
        logger.info("✅ Motor de Análisis Técnico: OPERATIVO")
        logger.info("✅ Indicadores calculados: EMA21, RSI14, MACD (3 componentes), Media de Volumen")
        logger.info("🚀 Sistema listo para la siguiente fase: Lógica de Señales de Trading")
        
    except PhoenixError as e:
        logger.error(f"Error del Proyecto Phoenix: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
