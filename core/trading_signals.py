"""
Lógica de Señales de Trading para el Proyecto Phoenix.

Este módulo implementa la detección inteligente de señales alcistas y bajistas
basada en la diferenciación entre estado y evento para evitar alertas redundantes.
Sigue las especificaciones exactas del documento Proyecto Phoenix punto 2.3.
"""

import pandas as pd
import logging
from typing import Optional, Dict, Any, Tuple
from enum import Enum

from utils.exceptions import AnalysisError, InsufficientDataError


class SignalType(Enum):
    """Enumeración de los tipos de señal posibles."""
    BULLISH_SIGNAL = "BULLISH_SIGNAL"
    BEARISH_SIGNAL = "BEARISH_SIGNAL"
    NO_SIGNAL = "NO_SIGNAL"


class TradingSignalsEngine:
    """
    Motor de detección de señales de trading que implementa lógica stateful.
    
    Este motor analiza las dos últimas velas del DataFrame enriquecido para
    detectar transiciones de estado y generar señales solo cuando las condiciones
    cambian de False a True, evitando alertas redundantes.
    """
    
    def __init__(self):
        """Inicializa el motor de señales de trading."""
        self.logger = logging.getLogger(__name__)
        
        # Columnas requeridas para el análisis
        self.required_columns = [
            'close', 'volume', 'EMA21', 'RSI14', 
            'MACD_Histogram', 'Volume_Avg20'
        ]
        
        self.logger.info("Motor de señales de trading inicializado")
    
    def analyze_signals(self, enriched_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analiza el DataFrame enriquecido y detecta señales de trading.
        
        Implementa la lógica stateful que diferencia entre estado y evento,
        generando señales solo en el momento exacto de la transición.
        
        Args:
            enriched_df: DataFrame con datos OHLCV e indicadores técnicos
            
        Returns:
            Diccionario con el resultado del análisis de señales
            
        Raises:
            AnalysisError: Si hay errores en el análisis
            InsufficientDataError: Si no hay suficientes datos
        """
        try:
            self.logger.info("Iniciando análisis de señales de trading")
            
            # Validar DataFrame de entrada
            self._validate_input_dataframe(enriched_df)
            
            # Verificar señal alcista
            bullish_signal, bullish_details = self._check_bullish_signal(enriched_df)
            
            # Verificar señal bajista
            bearish_signal, bearish_details = self._check_bearish_signal(enriched_df)
            
            # Determinar el resultado final
            final_signal = self._determine_final_signal(bullish_signal, bearish_signal)
            
            # Preparar resultado completo
            result = {
                'signal_type': final_signal,
                'timestamp': enriched_df.index[-1],
                'current_price': float(enriched_df['close'].iloc[-1]),
                'bullish_analysis': bullish_details,
                'bearish_analysis': bearish_details,
                'market_conditions': self._get_current_market_conditions(enriched_df)
            }
            
            self.logger.info(f"Análisis de señales completado: {final_signal.value}")
            return result
            
        except Exception as e:
            error_msg = f"Error durante el análisis de señales: {str(e)}"
            self.logger.error(error_msg)
            raise AnalysisError(error_msg) from e
    
    def _validate_input_dataframe(self, df: pd.DataFrame) -> None:
        """
        Valida que el DataFrame tenga la estructura correcta para el análisis.
        
        Args:
            df: DataFrame a validar
            
        Raises:
            InsufficientDataError: Si no hay suficientes datos
            AnalysisError: Si faltan columnas requeridas
        """
        # Verificar que hay al menos 2 filas (vela actual y anterior)
        if len(df) < 2:
            raise InsufficientDataError(
                f"Se requieren al menos 2 velas para el análisis de transición. "
                f"Solo hay {len(df)} disponibles"
            )
        
        # Verificar columnas requeridas
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            raise AnalysisError(
                f"Columnas faltantes para el análisis de señales: {missing_columns}"
            )
        
        # Verificar que las últimas 2 filas no tienen valores nulos en columnas críticas
        recent_data = df[self.required_columns].tail(2)
        null_counts = recent_data.isnull().sum()
        
        if null_counts.sum() > 0:
            null_info = dict(null_counts[null_counts > 0])
            raise AnalysisError(
                f"Valores nulos encontrados en las últimas 2 velas: {null_info}"
            )
        
        self.logger.debug("DataFrame validado para análisis de señales")
    
    def _check_bullish_signal(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """
        Verifica si se ha producido una señal alcista basada en transición de estado.
        
        Reglas según documento Proyecto Phoenix:
        - Precio de cierre > EMA21
        - RSI entre 30 y 50 
        - Histograma MACD > 0 (positivo)
        - Volumen > Media de volumen de 20 períodos
        
        La señal se activa solo si estas condiciones son TRUE en vela actual
        Y eran FALSE en vela anterior (detección de transición).
        
        Args:
            df: DataFrame con indicadores calculados
            
        Returns:
            Tupla con (señal_detectada, detalles_del_análisis)
        """
        self.logger.debug("Verificando condiciones alcistas")
        
        # Obtener las dos últimas velas
        current_candle = df.iloc[-1]  # Vela actual
        previous_candle = df.iloc[-2]  # Vela anterior
        
        # === CONDICIONES ALCISTAS - VELA ACTUAL ===
        current_bullish_conditions = {
            'price_above_ema': current_candle['close'] > current_candle['EMA21'],
            'rsi_in_range': 30 <= current_candle['RSI14'] <= 50,
            'macd_histogram_positive': current_candle['MACD_Histogram'] > 0,
            'volume_above_average': current_candle['volume'] > current_candle['Volume_Avg20']
        }
        
        # === CONDICIONES ALCISTAS - VELA ANTERIOR ===
        previous_bullish_conditions = {
            'price_above_ema': previous_candle['close'] > previous_candle['EMA21'],
            'rsi_in_range': 30 <= previous_candle['RSI14'] <= 50,
            'macd_histogram_positive': previous_candle['MACD_Histogram'] > 0,
            'volume_above_average': previous_candle['volume'] > previous_candle['Volume_Avg20']
        }
        
        # Verificar si TODAS las condiciones actuales son True
        all_current_conditions_met = all(current_bullish_conditions.values())
        
        # Verificar si TODAS las condiciones anteriores son False
        all_previous_conditions_unmet = not all(previous_bullish_conditions.values())
        
        # SEÑAL ALCISTA: Transición de FALSE a TRUE
        bullish_signal_detected = all_current_conditions_met and all_previous_conditions_unmet
        
        # Preparar detalles del análisis
        analysis_details = {
            'signal_detected': bullish_signal_detected,
            'current_conditions': current_bullish_conditions,
            'previous_conditions': previous_bullish_conditions,
            'all_current_met': all_current_conditions_met,
            'all_previous_unmet': all_previous_conditions_unmet,
            'transition_detected': all_current_conditions_met and all_previous_conditions_unmet,
            'current_values': {
                'close': float(current_candle['close']),
                'ema21': float(current_candle['EMA21']),
                'rsi14': float(current_candle['RSI14']),
                'macd_histogram': float(current_candle['MACD_Histogram']),
                'volume': float(current_candle['volume']),
                'volume_avg20': float(current_candle['Volume_Avg20'])
            },
            'previous_values': {
                'close': float(previous_candle['close']),
                'ema21': float(previous_candle['EMA21']),
                'rsi14': float(previous_candle['RSI14']),
                'macd_histogram': float(previous_candle['MACD_Histogram']),
                'volume': float(previous_candle['volume']),
                'volume_avg20': float(previous_candle['Volume_Avg20'])
            }
        }
        
        if bullish_signal_detected:
            self.logger.info("🟢 SEÑAL ALCISTA DETECTADA - Transición de condiciones identificada")
        else:
            if all_current_conditions_met:
                self.logger.debug("Condiciones alcistas actuales cumplidas, pero no hay transición")
            else:
                self.logger.debug("Condiciones alcistas actuales no cumplidas completamente")
        
        return bullish_signal_detected, analysis_details
    
    def _check_bearish_signal(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """
        Verifica si se ha producido una señal bajista basada en transición de estado.
        
        Reglas según documento Proyecto Phoenix:
        - Precio de cierre < EMA21
        - RSI entre 50 y 70
        - Histograma MACD < 0 (negativo)
        - Volumen > Media de volumen de 20 períodos
        
        La señal se activa solo si estas condiciones son TRUE en vela actual
        Y eran FALSE en vela anterior (detección de transición).
        
        Args:
            df: DataFrame con indicadores calculados
            
        Returns:
            Tupla con (señal_detectada, detalles_del_análisis)
        """
        self.logger.debug("Verificando condiciones bajistas")
        
        # Obtener las dos últimas velas
        current_candle = df.iloc[-1]  # Vela actual
        previous_candle = df.iloc[-2]  # Vela anterior
        
        # === CONDICIONES BAJISTAS - VELA ACTUAL ===
        current_bearish_conditions = {
            'price_below_ema': current_candle['close'] < current_candle['EMA21'],
            'rsi_in_range': 50 <= current_candle['RSI14'] <= 70,
            'macd_histogram_negative': current_candle['MACD_Histogram'] < 0,
            'volume_above_average': current_candle['volume'] > current_candle['Volume_Avg20']
        }
        
        # === CONDICIONES BAJISTAS - VELA ANTERIOR ===
        previous_bearish_conditions = {
            'price_below_ema': previous_candle['close'] < previous_candle['EMA21'],
            'rsi_in_range': 50 <= previous_candle['RSI14'] <= 70,
            'macd_histogram_negative': previous_candle['MACD_Histogram'] < 0,
            'volume_above_average': previous_candle['volume'] > previous_candle['Volume_Avg20']
        }
        
        # Verificar si TODAS las condiciones actuales son True
        all_current_conditions_met = all(current_bearish_conditions.values())
        
        # Verificar si TODAS las condiciones anteriores son False
        all_previous_conditions_unmet = not all(previous_bearish_conditions.values())
        
        # SEÑAL BAJISTA: Transición de FALSE a TRUE
        bearish_signal_detected = all_current_conditions_met and all_previous_conditions_unmet
        
        # Preparar detalles del análisis
        analysis_details = {
            'signal_detected': bearish_signal_detected,
            'current_conditions': current_bearish_conditions,
            'previous_conditions': previous_bearish_conditions,
            'all_current_met': all_current_conditions_met,
            'all_previous_unmet': all_previous_conditions_unmet,
            'transition_detected': all_current_conditions_met and all_previous_conditions_unmet,
            'current_values': {
                'close': float(current_candle['close']),
                'ema21': float(current_candle['EMA21']),
                'rsi14': float(current_candle['RSI14']),
                'macd_histogram': float(current_candle['MACD_Histogram']),
                'volume': float(current_candle['volume']),
                'volume_avg20': float(current_candle['Volume_Avg20'])
            },
            'previous_values': {
                'close': float(previous_candle['close']),
                'ema21': float(previous_candle['EMA21']),
                'rsi14': float(previous_candle['RSI14']),
                'macd_histogram': float(previous_candle['MACD_Histogram']),
                'volume': float(previous_candle['volume']),
                'volume_avg20': float(previous_candle['Volume_Avg20'])
            }
        }
        
        if bearish_signal_detected:
            self.logger.info("🔴 SEÑAL BAJISTA DETECTADA - Transición de condiciones identificada")
        else:
            if all_current_conditions_met:
                self.logger.debug("Condiciones bajistas actuales cumplidas, pero no hay transición")
            else:
                self.logger.debug("Condiciones bajistas actuales no cumplidas completamente")
        
        return bearish_signal_detected, analysis_details
    
    def _determine_final_signal(self, bullish_signal: bool, bearish_signal: bool) -> SignalType:
        """
        Determina la señal final basada en los resultados de análisis alcista y bajista.
        
        Args:
            bullish_signal: Si se detectó señal alcista
            bearish_signal: Si se detectó señal bajista
            
        Returns:
            Tipo de señal final
        """
        if bullish_signal and bearish_signal:
            # Caso teóricamente imposible, pero por robustez
            self.logger.warning("CONFLICTO: Señales alcista y bajista detectadas simultáneamente")
            return SignalType.NO_SIGNAL
        elif bullish_signal:
            return SignalType.BULLISH_SIGNAL
        elif bearish_signal:
            return SignalType.BEARISH_SIGNAL
        else:
            return SignalType.NO_SIGNAL
    
    def _get_current_market_conditions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Obtiene un resumen de las condiciones actuales del mercado.
        
        Args:
            df: DataFrame con indicadores
            
        Returns:
            Diccionario con condiciones del mercado
        """
        current_candle = df.iloc[-1]
        
        # Determinar tendencia basada en EMA
        price_vs_ema = "ABOVE" if current_candle['close'] > current_candle['EMA21'] else "BELOW"
        
        # Categorizar RSI
        rsi_value = current_candle['RSI14']
        if rsi_value < 30:
            rsi_zone = "OVERSOLD"
        elif rsi_value > 70:
            rsi_zone = "OVERBOUGHT"
        elif 30 <= rsi_value <= 50:
            rsi_zone = "NEUTRAL_BEARISH"
        else:  # 50 < rsi <= 70
            rsi_zone = "NEUTRAL_BULLISH"
        
        # Determinar momentum MACD
        macd_momentum = "POSITIVE" if current_candle['MACD_Histogram'] > 0 else "NEGATIVE"
        
        # Analizar volumen
        volume_ratio = current_candle['volume'] / current_candle['Volume_Avg20']
        volume_status = "HIGH" if volume_ratio > 1.0 else "LOW"
        
        return {
            'price_vs_ema': price_vs_ema,
            'rsi_zone': rsi_zone,
            'rsi_value': float(rsi_value),
            'macd_momentum': macd_momentum,
            'macd_histogram': float(current_candle['MACD_Histogram']),
            'volume_status': volume_status,
            'volume_ratio': float(volume_ratio),
            'current_price': float(current_candle['close']),
            'ema21_value': float(current_candle['EMA21'])
        }
    
    def get_signal_explanation(self, analysis_result: Dict[str, Any]) -> str:
        """
        Genera una explicación detallada de la señal para logging o notificación.
        
        Args:
            analysis_result: Resultado del análisis de señales
            
        Returns:
            Explicación textual de la señal
        """
        signal_type = analysis_result['signal_type']
        market_conditions = analysis_result['market_conditions']
        
        if signal_type == SignalType.BULLISH_SIGNAL:
            explanation = (
                f"🟢 SEÑAL ALCISTA DETECTADA:\n"
                f"• Precio ${market_conditions['current_price']:,.2f} cruzó ARRIBA de EMA21 ${market_conditions['ema21_value']:,.2f}\n"
                f"• RSI {market_conditions['rsi_value']:.1f} en zona {market_conditions['rsi_zone']}\n"
                f"• MACD Histograma {market_conditions['macd_momentum']} ({market_conditions['macd_histogram']:+.2f})\n"
                f"• Volumen {market_conditions['volume_status']} (ratio: {market_conditions['volume_ratio']:.2f}x)"
            )
        elif signal_type == SignalType.BEARISH_SIGNAL:
            explanation = (
                f"🔴 SEÑAL BAJISTA DETECTADA:\n"
                f"• Precio ${market_conditions['current_price']:,.2f} cruzó DEBAJO de EMA21 ${market_conditions['ema21_value']:,.2f}\n"
                f"• RSI {market_conditions['rsi_value']:.1f} en zona {market_conditions['rsi_zone']}\n"
                f"• MACD Histograma {market_conditions['macd_momentum']} ({market_conditions['macd_histogram']:+.2f})\n"
                f"• Volumen {market_conditions['volume_status']} (ratio: {market_conditions['volume_ratio']:.2f}x)"
            )
        else:
            explanation = (
                f"⚪ SIN SEÑAL RELEVANTE:\n"
                f"• Precio ${market_conditions['current_price']:,.2f} vs EMA21 ${market_conditions['ema21_value']:,.2f} ({market_conditions['price_vs_ema']})\n"
                f"• RSI {market_conditions['rsi_value']:.1f} en zona {market_conditions['rsi_zone']}\n"
                f"• MACD Histograma {market_conditions['macd_momentum']} ({market_conditions['macd_histogram']:+.2f})\n"
                f"• Volumen {market_conditions['volume_status']} (ratio: {market_conditions['volume_ratio']:.2f}x)\n"
                f"• No se detectó transición en las condiciones de entrada"
            )
        
        return explanation
