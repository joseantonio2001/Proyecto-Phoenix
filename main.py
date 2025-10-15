"""
Script principal del Proyecto Phoenix - Fase I Completa.

Demuestra la integración completa del conector del exchange, motor de análisis técnico
y la lógica de señales de trading según las especificaciones del documento "Proyecto Phoenix".
"""

import asyncio
import logging

from utils.config_manager import ConfigManager
from utils.logger import setup_logging
from core.exchange_connector import ExchangeConnector
from core.analysis_engine import TechnicalAnalysisEngine
from core.trading_signals import TradingSignalsEngine, SignalType
from utils.exceptions import PhoenixError


async def main():
    """
    Función principal que demuestra la integración completa de la Fase I.
    Pipeline: Exchange → Análisis Técnico → Señales de Trading
    """
    try:
        # Inicializar configuración
        config = ConfigManager()
        
        # Configurar logging
        logger = setup_logging(config)
        logger.info("=== PROYECTO PHOENIX - FASE I: NÚCLEO DE ANÁLISIS COMPLETO ===")
        logger.info("Iniciando pipeline completo: Conector → Análisis → Señales...")
        
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
        
        # === PASO 3: LÓGICA DE SEÑALES DE TRADING ===
        logger.info("--- PASO 3: INICIALIZANDO MOTOR DE SEÑALES DE TRADING ---")
        signals_engine = TradingSignalsEngine()
        
        logger.info("Analizando señales de trading con lógica stateful...")
        signals_result = signals_engine.analyze_signals(enriched_df)
        
        # === RESULTADOS DEL ANÁLISIS DE SEÑALES ===
        logger.info("=== ANÁLISIS DE SEÑALES COMPLETADO ===")
        signal_type = signals_result['signal_type']
        
        # Generar explicación detallada
        signal_explanation = signals_engine.get_signal_explanation(signals_result)
        logger.info("=== RESULTADO DE LA DETECCIÓN DE SEÑALES ===")
        logger.info(f"\n{signal_explanation}")
        
        # === DETALLES TÉCNICOS DE LA SEÑAL ===
        logger.info("=== DETALLES TÉCNICOS DEL ANÁLISIS ===")
        
        if signal_type == SignalType.BULLISH_SIGNAL:
            logger.info("🟢 SEÑAL ALCISTA DETECTADA")
            bullish_details = signals_result['bullish_analysis']
            logger.info("Condiciones actuales cumplidas:")
            for condition, met in bullish_details['current_conditions'].items():
                status = "✅" if met else "❌"
                logger.info(f"  {status} {condition}")
            
            logger.info("Transición detectada: Las condiciones pasaron de NO cumplidas a SÍ cumplidas")
            
        elif signal_type == SignalType.BEARISH_SIGNAL:
            logger.info("🔴 SEÑAL BAJISTA DETECTADA")
            bearish_details = signals_result['bearish_analysis']
            logger.info("Condiciones actuales cumplidas:")
            for condition, met in bearish_details['current_conditions'].items():
                status = "✅" if met else "❌"
                logger.info(f"  {status} {condition}")
            
            logger.info("Transición detectada: Las condiciones pasaron de NO cumplidas a SÍ cumplidas")
            
        else:
            logger.info("⚪ SIN SEÑAL RELEVANTE EN EL CICLO ACTUAL")
            logger.info("Razón: No se detectó transición de estado en las condiciones de entrada")
            
            # Mostrar estado actual de condiciones alcistas
            bullish_details = signals_result['bullish_analysis']
            logger.info("Estado actual de condiciones alcistas:")
            for condition, met in bullish_details['current_conditions'].items():
                status = "✅" if met else "❌"
                logger.info(f"  {status} {condition}")
            
            # Mostrar estado actual de condiciones bajistas
            bearish_details = signals_result['bearish_analysis']
            logger.info("Estado actual de condiciones bajistas:")
            for condition, met in bearish_details['current_conditions'].items():
                status = "✅" if met else "❌"
                logger.info(f"  {status} {condition}")
        
        # === VALORES DE INDICADORES ACTUALES ===
        logger.info("=== VALORES DE INDICADORES EN VELA ACTUAL ===")
        market_conditions = signals_result['market_conditions']
        logger.info(f"Timestamp: {signals_result['timestamp']}")
        logger.info(f"Precio actual: ${market_conditions['current_price']:,.2f}")
        logger.info(f"EMA21: ${market_conditions['ema21_value']:,.2f} ({market_conditions['price_vs_ema']})")
        logger.info(f"RSI14: {market_conditions['rsi_value']:.2f} ({market_conditions['rsi_zone']})")
        logger.info(f"MACD Histograma: {market_conditions['macd_histogram']:+.4f} ({market_conditions['macd_momentum']})")
        logger.info(f"Volumen: {market_conditions['volume_ratio']:.2f}x promedio ({market_conditions['volume_status']})")
        
        # === COMPARACIÓN ENTRE VELAS (DETECCIÓN DE TRANSICIÓN) ===
        logger.info("=== ANÁLISIS DE TRANSICIÓN ENTRE VELAS ===")
        
        if signal_type != SignalType.NO_SIGNAL:
            # Hay señal - mostrar la transición
            if signal_type == SignalType.BULLISH_SIGNAL:
                details = signals_result['bullish_analysis']
                logger.info("Transición Alcista Detectada:")
            else:
                details = signals_result['bearish_analysis']
                logger.info("Transición Bajista Detectada:")
            
            logger.info(f"Vela anterior: Condiciones NO cumplidas ({not details['all_previous_met']})")
            logger.info(f"Vela actual: Condiciones SÍ cumplidas ({details['all_current_met']})")
            logger.info("✅ EVENTO DE TRANSICIÓN CONFIRMADO")
        else:
            logger.info("No se detectó transición válida:")
            logger.info("• Las condiciones pueden estar cumplidas en ambas velas (sin evento)")
            logger.info("• O las condiciones no están completamente cumplidas en la vela actual")
            logger.info("• La lógica stateful evita alertas redundantes")
        
        # === ESTADO FINAL DEL SISTEMA ===
        logger.info("=== FASE I - NÚCLEO DE ANÁLISIS: COMPLETADO EXITOSAMENTE ===")
        logger.info("✅ Conector del Exchange: OPERATIVO")
        logger.info("✅ Motor de Análisis Técnico: OPERATIVO")
        logger.info("✅ Motor de Señales de Trading: OPERATIVO")
        logger.info("✅ Lógica Stateful: Diferenciación entre estado y evento implementada")
        logger.info(f"🎯 Resultado final del ciclo: {signal_type.value}")
        logger.info("🚀 Sistema listo para la siguiente fase: Interfaz de Usuario y Bot de Telegram")
        
    except PhoenixError as e:
        logger.error(f"Error del Proyecto Phoenix: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
