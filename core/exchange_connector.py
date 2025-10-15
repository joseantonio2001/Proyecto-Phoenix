"""
Conector de Exchange para el Proyecto Phoenix.

Este módulo encapsula toda la interacción con ccxt para hacer el sistema 
agnóstico al exchange específico. Implementa gestión robusta de errores,
validación crítica de datos y configurabilidad.
"""

import ccxt
import pandas as pd
import time
from typing import Optional, Tuple, List, Dict, Any
import logging
from datetime import datetime, timedelta

from utils.exceptions import (
    ExchangeConnectionError,
    DataValidationError,
    RateLimitError,
    InsufficientDataError
)
from utils.config_manager import ConfigManager


class ExchangeConnector:
    """
    Conector robusto y configurable para exchanges de criptomonedas usando ccxt.
    
    Esta clase encapsula toda la interacción con la biblioteca ccxt, proporcionando
    una interfaz limpia y agnóstica al exchange para el resto del sistema.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Inicializa el conector del exchange.
        
        Args:
            config_manager: Instancia del gestor de configuración
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self._exchange: Optional[ccxt.Exchange] = None
        self._initialize_exchange()
    
    def _initialize_exchange(self) -> None:
        """
        Inicializa la conexión con el exchange basado en la configuración.
        
        Raises:
            ExchangeConnectionError: Si no se puede inicializar el exchange
        """
        try:
            exchange_id = self.config.get_exchange_id()
            exchange_class = getattr(ccxt, exchange_id)
            
            # Configuración básica del exchange
            self._exchange = exchange_class({
                'apiKey': self.config.get_api_key(),
                'secret': self.config.get_api_secret(),
                'timeout': 30000,  # 30 segundos timeout
                'enableRateLimit': True,  # Habilitar rate limiting automático
                'sandbox': False,  # Cambiar a True para testing
            })
            
            # Verificar que el exchange esté disponible
            if not self._exchange.has['fetchOHLCV']:
                raise ExchangeConnectionError(
                    f"El exchange {exchange_id} no soporta fetchOHLCV"
                )
            
            self.logger.info(f"Exchange {exchange_id} inicializado correctamente")
            
        except AttributeError:
            raise ExchangeConnectionError(
                f"Exchange ID no válido: {self.config.get_exchange_id()}"
            )
        except Exception as e:
            raise ExchangeConnectionError(f"Error inicializando exchange: {str(e)}")
    
    def fetch_ohlcv_data(
        self, 
        symbol: str, 
        timeframe: str, 
        limit: int = 200,
        max_retries: int = 3
    ) -> pd.DataFrame:
        """
        Obtiene datos OHLCV del exchange con gestión robusta de errores.
        
        Args:
            symbol: Par de trading (ej: 'BTC/USDC')
            timeframe: Temporalidad (ej: '2h', '1d')
            limit: Número de velas a obtener
            max_retries: Número máximo de reintentos
            
        Returns:
            DataFrame con datos OHLCV validados
            
        Raises:
            ExchangeConnectionError: Error de conexión persistente
            RateLimitError: Límite de velocidad excedido
            DataValidationError: Datos inválidos recibidos
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                self.logger.info(
                    f"Obteniendo datos OHLCV - Símbolo: {symbol}, "
                    f"Timeframe: {timeframe}, Límite: {limit} (Intento {attempt + 1})"
                )
                
                # Obtener datos del exchange
                ohlcv_data = self._exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=limit
                )
                
                # Convertir a DataFrame
                df = self._convert_to_dataframe(ohlcv_data)
                
                # Validar datos críticos
                validated_df = self._validate_ohlcv_data(df, symbol, timeframe, limit)
                
                self.logger.info(
                    f"Datos OHLCV obtenidos y validados exitosamente. "
                    f"Filas: {len(validated_df)}"
                )
                
                return validated_df
                
            except ccxt.RateLimitExceeded as e:
                last_exception = e
                wait_time = self._calculate_backoff_time(attempt)
                self.logger.warning(
                    f"Rate limit excedido en intento {attempt + 1}. "
                    f"Esperando {wait_time} segundos..."
                )
                
                if attempt < max_retries:
                    time.sleep(wait_time)
                    continue
                else:
                    raise RateLimitError(
                        f"Rate limit excedido después de {max_retries} intentos"
                    )
                    
            except ccxt.NetworkError as e:
                last_exception = e
                wait_time = self._calculate_backoff_time(attempt)
                self.logger.warning(
                    f"Error de red en intento {attempt + 1}: {str(e)}. "
                    f"Reintentando en {wait_time} segundos..."
                )
                
                if attempt < max_retries:
                    time.sleep(wait_time)
                    continue
                else:
                    raise ExchangeConnectionError(
                        f"Error de red persistente después de {max_retries} intentos: {str(e)}"
                    )
                    
            except ccxt.ExchangeError as e:
                last_exception = e
                self.logger.error(f"Error del exchange en intento {attempt + 1}: {str(e)}")
                
                # Para errores del exchange, no reintentar (pueden ser permanentes)
                raise ExchangeConnectionError(f"Error del exchange: {str(e)}")
                
            except Exception as e:
                last_exception = e
                self.logger.error(f"Error inesperado en intento {attempt + 1}: {str(e)}")
                
                if attempt < max_retries:
                    wait_time = self._calculate_backoff_time(attempt)
                    time.sleep(wait_time)
                    continue
                else:
                    raise ExchangeConnectionError(f"Error inesperado: {str(e)}")
        
        # Si llegamos aquí, todos los intentos fallaron
        raise ExchangeConnectionError(
            f"Falló la obtención de datos después de {max_retries} intentos. "
            f"Último error: {str(last_exception)}"
        )
    
    def _convert_to_dataframe(self, ohlcv_data: List[List]) -> pd.DataFrame:
        """
        Convierte los datos OHLCV de ccxt a un DataFrame de pandas.
        
        Args:
            ohlcv_data: Lista de listas con datos OHLCV
            
        Returns:
            DataFrame estructurado con índice de tiempo
        """
        # Crear DataFrame con columnas apropiadas
        df = pd.DataFrame(
            ohlcv_data, 
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        # Convertir timestamp a datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Establecer timestamp como índice
        df.set_index('timestamp', inplace=True)
        
        # Asegurar que todas las columnas numéricas sean float
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_columns] = df[numeric_columns].astype(float)
        
        return df
    
    def _validate_ohlcv_data(
        self, 
        df: pd.DataFrame, 
        symbol: str, 
        timeframe: str, 
        expected_limit: int
    ) -> pd.DataFrame:
        """
        Realiza validación crítica de los datos OHLCV.
        
        Args:
            df: DataFrame con datos OHLCV
            symbol: Símbolo del par de trading
            timeframe: Temporalidad solicitada
            expected_limit: Número esperado de velas
            
        Returns:
            DataFrame validado
            
        Raises:
            DataValidationError: Si los datos no pasan la validación
        """
        validation_errors = []
        
        # 1. Verificar datos completos
        actual_rows = len(df)
        if actual_rows < expected_limit * 0.9:  # Permitir 10% de tolerancia
            validation_errors.append(
                f"Datos insuficientes: esperados ~{expected_limit}, "
                f"recibidos {actual_rows}"
            )
        
        # 2. Verificar ausencia de valores nulos o NaN
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            null_info = dict(null_counts[null_counts > 0])
            validation_errors.append(f"Valores nulos encontrados: {null_info}")
        
        # 3. Verificar continuidad temporal
        time_diffs = df.index.to_series().diff().dropna()
        expected_diff = self._get_timeframe_delta(timeframe)
        
        # Tolerancia del 10% para diferencias temporales
        tolerance = expected_diff * 0.1
        irregular_gaps = time_diffs[
            abs(time_diffs - expected_diff) > tolerance
        ]
        
        if len(irregular_gaps) > 0:
            validation_errors.append(
                f"Gaps temporales irregulares detectados: {len(irregular_gaps)} gaps"
            )
        
        # 4. Verificar valores atípicos básicos
        price_columns = ['open', 'high', 'low', 'close']
        
        # Verificar precios negativos o zero
        for col in price_columns:
            invalid_prices = df[df[col] <= 0]
            if len(invalid_prices) > 0:
                validation_errors.append(
                    f"Precios inválidos en columna {col}: "
                    f"{len(invalid_prices)} valores <= 0"
                )
        
        # Verificar relaciones OHLC lógicas
        illogical_candles = df[
            (df['high'] < df['low']) | 
            (df['high'] < df['open']) | 
            (df['high'] < df['close']) |
            (df['low'] > df['open']) | 
            (df['low'] > df['close'])
        ]
        
        if len(illogical_candles) > 0:
            validation_errors.append(
                f"Velas con relaciones OHLC ilógicas: {len(illogical_candles)}"
            )
        
        # Verificar volumen zero en velas con movimiento significativo
        price_change = abs(df['close'] - df['open']) / df['open']
        significant_moves = df[price_change > 0.01]  # Movimientos > 1%
        zero_volume_moves = significant_moves[significant_moves['volume'] == 0]
        
        if len(zero_volume_moves) > 0:
            validation_errors.append(
                f"Velas con movimiento significativo pero volumen zero: "
                f"{len(zero_volume_moves)}"
            )
        
        # Si hay errores de validación, abortar
        if validation_errors:
            error_msg = f"Validación de datos fallida para {symbol} {timeframe}:\n"
            error_msg += "\n".join(f"- {error}" for error in validation_errors)
            
            self.logger.error(error_msg)
            raise DataValidationError(error_msg)
        
        self.logger.info(f"Validación de datos exitosa para {symbol} {timeframe}")
        return df
    
    def _get_timeframe_delta(self, timeframe: str) -> timedelta:
        """
        Convierte un timeframe de ccxt a un timedelta.
        
        Args:
            timeframe: Timeframe en formato ccxt (ej: '1h', '2h', '1d')
            
        Returns:
            Timedelta correspondiente
        """
        timeframe_mapping = {
            '1m': timedelta(minutes=1),
            '5m': timedelta(minutes=5),
            '15m': timedelta(minutes=15),
            '30m': timedelta(minutes=30),
            '1h': timedelta(hours=1),
            '2h': timedelta(hours=2),
            '4h': timedelta(hours=4),
            '6h': timedelta(hours=6),
            '8h': timedelta(hours=8),
            '12h': timedelta(hours=12),
            '1d': timedelta(days=1),
            '3d': timedelta(days=3),
            '1w': timedelta(weeks=1),
        }
        
        return timeframe_mapping.get(
            timeframe, 
            timedelta(hours=1)  # Default fallback
        )
    
    def _calculate_backoff_time(self, attempt: int) -> float:
        """
        Calcula el tiempo de espera para reintento con backoff exponencial.
        
        Args:
            attempt: Número de intento (0-based)
            
        Returns:
            Tiempo de espera en segundos
        """
        # Backoff exponencial: 2^attempt + jitter
        import random
        base_wait = 2 ** attempt
        jitter = random.uniform(0, 1)
        return min(base_wait + jitter, 60)  # Máximo 60 segundos
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Obtiene información del exchange.
        
        Returns:
            Diccionario con información del exchange
        """
        return {
            'id': self._exchange.id,
            'name': self._exchange.name,
            'has_fetch_ohlcv': self._exchange.has['fetchOHLCV'],
            'timeframes': self._exchange.timeframes,
            'rate_limit': self._exchange.rateLimit,
        }
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con el exchange.
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            self._exchange.load_markets()
            self.logger.info("Test de conexión exitoso")
            return True
        except Exception as e:
            self.logger.error(f"Test de conexión fallido: {str(e)}")
            return False
