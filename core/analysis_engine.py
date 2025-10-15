"""
Motor de Análisis Técnico para el Proyecto Phoenix.

Este módulo implementa el corazón computacional del sistema, responsable de
calcular todos los indicadores técnicos necesarios para la estrategia de trading
utilizando pandas-ta según las especificaciones del documento.
"""

import pandas as pd
import pandas_ta as ta
import logging
from typing import Optional, Dict, Any
import numpy as np

from utils.config_manager import ConfigManager
from utils.exceptions import AnalysisError, InsufficientDataError


class TechnicalAnalysisEngine:
    """
    Motor de análisis técnico que enriquece los datos OHLCV con indicadores.
    
    Este motor recibe un DataFrame de pandas con datos OHLCV y lo enriquece
    añadiendo todas las columnas de indicadores técnicos necesarios para
    la estrategia de trading definida en el documento Proyecto Phoenix.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Inicializa el motor de análisis técnico.
        
        Args:
            config_manager: Instancia del gestor de configuración
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Cargar parámetros de configuración
        self.ema_period = self.config.get_ema_period()
        self.rsi_period = self.config.get_rsi_period()
        self.macd_fast = self.config.get_macd_fast()
        self.macd_slow = self.config.get_macd_slow()
        self.macd_signal = self.config.get_macd_signal()
        self.volume_avg_period = self.config.get_volume_avg_period()
        
        self.logger.info(
            f"Motor de análisis inicializado - EMA: {self.ema_period}, "
            f"RSI: {self.rsi_period}, MACD: {self.macd_fast}/{self.macd_slow}/{self.macd_signal}, "
            f"Vol Avg: {self.volume_avg_period}"
        )
    
    def enrich_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriquece el DataFrame OHLCV con todos los indicadores técnicos.
        
        Args:
            df: DataFrame con datos OHLCV (timestamp como índice)
            
        Returns:
            DataFrame enriquecido con indicadores técnicos
            
        Raises:
            AnalysisError: Si hay errores en el cálculo de indicadores
            InsufficientDataError: Si no hay suficientes datos para los cálculos
        """
        try:
            self.logger.info("Iniciando enriquecimiento del DataFrame con indicadores técnicos")
            
            # Validar DataFrame de entrada
            enriched_df = self._validate_input_dataframe(df.copy())
            
            # Calcular todos los indicadores técnicos
            enriched_df = self._calculate_ema(enriched_df)
            enriched_df = self._calculate_rsi(enriched_df)
            enriched_df = self._calculate_macd(enriched_df)
            enriched_df = self._calculate_volume_average(enriched_df)
            
            # Validar que todos los indicadores se calcularon correctamente
            self._validate_indicators(enriched_df)
            
            self.logger.info(
                f"DataFrame enriquecido exitosamente. "
                f"Columnas añadidas: {self._get_indicator_columns()}"
            )
            
            return enriched_df
            
        except Exception as e:
            error_msg = f"Error durante el enriquecimiento del DataFrame: {str(e)}"
            self.logger.error(error_msg)
            raise AnalysisError(error_msg) from e
    
    def _validate_input_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida el DataFrame de entrada para el análisis técnico.
        
        Args:
            df: DataFrame OHLCV a validar
            
        Returns:
            DataFrame validado
            
        Raises:
            InsufficientDataError: Si no hay suficientes datos
            AnalysisError: Si la estructura del DataFrame es incorrecta
        """
        # Verificar columnas requeridas
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise AnalysisError(
                f"Columnas faltantes en el DataFrame: {missing_columns}. "
                f"Se requieren: {required_columns}"
            )
        
        # Verificar que el índice sea datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            raise AnalysisError(
                "El índice del DataFrame debe ser DatetimeIndex (timestamp)"
            )
        
        # Verificar datos suficientes para el indicador más largo
        max_period = max(
            self.ema_period,
            self.rsi_period,
            self.macd_slow + self.macd_signal,  # MACD necesita slow + signal
            self.volume_avg_period
        )
        
        if len(df) < max_period + 10:  # +10 para margen de seguridad
            raise InsufficientDataError(
                f"Datos insuficientes para calcular indicadores. "
                f"Se requieren al menos {max_period + 10} filas, "
                f"pero solo hay {len(df)} disponibles"
            )
        
        # Verificar que no hay valores nulos en las columnas OHLCV
        null_counts = df[required_columns].isnull().sum()
        if null_counts.sum() > 0:
            null_info = dict(null_counts[null_counts > 0])
            raise AnalysisError(f"Valores nulos encontrados en OHLCV: {null_info}")
        
        self.logger.debug(f"DataFrame validado: {len(df)} filas con {len(df.columns)} columnas")
        return df
    
    def _calculate_ema(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula la Media Móvil Exponencial (EMA) usando pandas-ta.
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            DataFrame con columna EMA añadida
        """
        self.logger.debug(f"Calculando EMA con período {self.ema_period}")
        
        # Calcular EMA usando pandas-ta
        # La función ema de pandas-ta añade automáticamente la columna al DataFrame
        df.ta.ema(length=self.ema_period, append=True)
        
        # La columna se nombra automáticamente como EMA_<period>
        ema_column = f'EMA_{self.ema_period}'
        
        if ema_column not in df.columns:
            raise AnalysisError(f"Error calculando EMA: columna {ema_column} no creada")
        
        # Renombrar para consistencia con la estrategia
        df.rename(columns={ema_column: 'EMA21'}, inplace=True)
        
        self.logger.debug(f"EMA calculada exitosamente. Primeros valores no nulos desde fila {self.ema_period-1}")
        return df
    
    def _calculate_rsi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula el Índice de Fuerza Relativa (RSI) usando pandas-ta.
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            DataFrame con columna RSI añadida
        """
        self.logger.debug(f"Calculando RSI con período {self.rsi_period}")
        
        # Calcular RSI usando pandas-ta
        df.ta.rsi(length=self.rsi_period, append=True)
        
        # La columna se nombra automáticamente como RSI_<period>
        rsi_column = f'RSI_{self.rsi_period}'
        
        if rsi_column not in df.columns:
            raise AnalysisError(f"Error calculando RSI: columna {rsi_column} no creada")
        
        # Renombrar para consistencia con la estrategia
        df.rename(columns={rsi_column: 'RSI14'}, inplace=True)
        
        self.logger.debug(f"RSI calculado exitosamente. Rango esperado: 0-100")
        return df
    
    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula el MACD (Convergencia/Divergencia de Medias Móviles) usando pandas-ta.
        
        Genera automáticamente las tres columnas: línea MACD, línea de señal e histograma.
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            DataFrame con columnas MACD añadidas
        """
        self.logger.debug(
            f"Calculando MACD con parámetros fast={self.macd_fast}, "
            f"slow={self.macd_slow}, signal={self.macd_signal}"
        )
        
        # Calcular MACD usando pandas-ta
        # Esto genera automáticamente las tres columnas
        df.ta.macd(
            fast=self.macd_fast,
            slow=self.macd_slow,
            signal=self.macd_signal,
            append=True
        )
        
        # Las columnas se nombran automáticamente como MACD_<fast>_<slow>_<signal>
        macd_base = f'MACD_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}'
        macd_line_col = f'{macd_base}'
        macd_histogram_col = f'MACDh_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}'
        macd_signal_col = f'MACDs_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}'
        
        # Verificar que las columnas fueron creadas
        expected_columns = [macd_line_col, macd_histogram_col, macd_signal_col]
        missing = [col for col in expected_columns if col not in df.columns]
        
        if missing:
            raise AnalysisError(f"Error calculando MACD: columnas faltantes {missing}")
        
        # Renombrar columnas para consistencia con la estrategia
        df.rename(columns={
            macd_line_col: 'MACD',
            macd_signal_col: 'MACD_Signal', 
            macd_histogram_col: 'MACD_Histogram'
        }, inplace=True)
        
        self.logger.debug("MACD calculado exitosamente con las tres componentes")
        return df
    
    def _calculate_volume_average(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula la media móvil simple del volumen usando pandas.
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            DataFrame con columna de media de volumen añadida
        """
        self.logger.debug(f"Calculando media de volumen con período {self.volume_avg_period}")
        
        # Calcular media móvil simple del volumen usando pandas
        df['Volume_Avg20'] = df['volume'].rolling(window=self.volume_avg_period).mean()
        
        # Verificar que la columna fue creada correctamente
        if 'Volume_Avg20' not in df.columns:
            raise AnalysisError("Error calculando media de volumen: columna no creada")
        
        # Verificar que hay valores válidos (no todos NaN)
        valid_values = df['Volume_Avg20'].notna().sum()
        if valid_values == 0:
            raise AnalysisError("Error: todos los valores de la media de volumen son NaN")
        
        self.logger.debug(
            f"Media de volumen calculada exitosamente. "
            f"Valores válidos: {valid_values}/{len(df)}"
        )
        return df
    
    def _validate_indicators(self, df: pd.DataFrame) -> None:
        """
        Valida que todos los indicadores fueron calculados correctamente.
        
        Args:
            df: DataFrame enriquecido
            
        Raises:
            AnalysisError: Si algún indicador no fue calculado correctamente
        """
        expected_indicators = ['EMA21', 'RSI14', 'MACD', 'MACD_Signal', 'MACD_Histogram', 'Volume_Avg20']
        missing_indicators = [col for col in expected_indicators if col not in df.columns]
        
        if missing_indicators:
            raise AnalysisError(f"Indicadores faltantes después del cálculo: {missing_indicators}")
        
        # Verificar que las últimas filas tienen valores válidos (no NaN)
        # Tomamos las últimas 10 filas para verificar
        recent_data = df[expected_indicators].tail(10)
        
        for indicator in expected_indicators:
            recent_values = recent_data[indicator]
            valid_recent = recent_values.notna().sum()
            
            if valid_recent == 0:
                raise AnalysisError(
                    f"El indicador {indicator} no tiene valores válidos en las últimas 10 filas"
                )
        
        # Validaciones específicas de rangos
        self._validate_rsi_range(df)
        
        self.logger.debug("Todos los indicadores validados exitosamente")
    
    def _validate_rsi_range(self, df: pd.DataFrame) -> None:
        """
        Valida que los valores del RSI estén en el rango esperado (0-100).
        
        Args:
            df: DataFrame con RSI calculado
        """
        rsi_values = df['RSI14'].dropna()
        
        if len(rsi_values) > 0:
            min_rsi = rsi_values.min()
            max_rsi = rsi_values.max()
            
            if min_rsi < 0 or max_rsi > 100:
                self.logger.warning(
                    f"Valores RSI fuera de rango: mín={min_rsi:.2f}, máx={max_rsi:.2f}"
                )
    
    def _get_indicator_columns(self) -> list:
        """
        Retorna la lista de columnas de indicadores que añade este motor.
        
        Returns:
            Lista de nombres de columnas de indicadores
        """
        return ['EMA21', 'RSI14', 'MACD', 'MACD_Signal', 'MACD_Histogram', 'Volume_Avg20']
    
    def get_latest_indicators_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Obtiene un resumen de los valores de los indicadores en la última vela.
        
        Args:
            df: DataFrame enriquecido con indicadores
            
        Returns:
            Diccionario con valores actuales de todos los indicadores
        """
        if len(df) == 0:
            return {}
        
        latest_row = df.iloc[-1]
        
        return {
            'timestamp': df.index[-1].strftime('%Y-%m-%d %H:%M:%S'),
            'close_price': float(latest_row['close']),
            'ema21': float(latest_row['EMA21']) if pd.notna(latest_row['EMA21']) else None,
            'rsi14': float(latest_row['RSI14']) if pd.notna(latest_row['RSI14']) else None,
            'macd': float(latest_row['MACD']) if pd.notna(latest_row['MACD']) else None,
            'macd_signal': float(latest_row['MACD_Signal']) if pd.notna(latest_row['MACD_Signal']) else None,
            'macd_histogram': float(latest_row['MACD_Histogram']) if pd.notna(latest_row['MACD_Histogram']) else None,
            'volume': float(latest_row['volume']),
            'volume_avg20': float(latest_row['Volume_Avg20']) if pd.notna(latest_row['Volume_Avg20']) else None,
        }
    
    def get_configuration_summary(self) -> Dict[str, int]:
        """
        Obtiene un resumen de la configuración actual de los indicadores.
        
        Returns:
            Diccionario con los parámetros de configuración
        """
        return {
            'ema_period': self.ema_period,
            'rsi_period': self.rsi_period,
            'macd_fast': self.macd_fast,
            'macd_slow': self.macd_slow,
            'macd_signal': self.macd_signal,
            'volume_avg_period': self.volume_avg_period,
        }
