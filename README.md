# Proyecto Phoenix

## Descripción

Proyecto Phoenix es un sistema automatizado de análisis y operaciones para el mercado de criptomonedas, con un enfoque inicial en el par Bitcoin-USD Coin (BTC/USDC). El sistema está diseñado para ser modular, robusto y escalable, comenzando como una herramienta avanzada de análisis y alertas, con una hoja de ruta clara hacia la ejecución de operaciones totalmente autónoma.

El proyecto implementa una arquitectura inspirada en microservicios que promueve la modularidad, la mantenibilidad y la escalabilidad futura, permitiendo que cada componente sea desarrollado, probado y mantenido de forma independiente.

## Estado Actual

✅ **Fase I - Punto 2.1: Construcción del Conector del Exchange - COMPLETADO**

El proyecto ha completado exitosamente la implementación del punto "2.1. Construcción del Conector del Exchange" de la Fase I. La funcionalidad incluye:

- **Conexión robusta al exchange** mediante encapsulación completa de ccxt
- **Obtención y validación crítica de datos OHLCV** con 6 niveles de verificación
- **Gestión exhaustiva de errores** con reintentos automáticos y backoff exponencial  
- **Sistema de configuración centralizado** para máxima flexibilidad
- **Logging detallado** para monitorización y debugging
- **Calidad de producción** con type hints, documentación completa y cumplimiento PEP 8

✅ **Fase I - Punto 2.2: El Motor de Análisis Técnico - COMPLETADO**

El sistema ahora enriquece los datos OHLCV con un conjunto configurable de indicadores técnicos utilizando pandas-ta:

- **EMA21** (Media Móvil Exponencial) con período configurable
- **RSI14** (Índice de Fuerza Relativa) con período configurable  
- **MACD** (Convergencia/Divergencia de Medias Móviles) con tres componentes: línea principal, señal e histograma
- **Media de Volumen** (promedio móvil simple del volumen) con período configurable
- **Validación automática** de calidad e integridad de indicadores
- **Configuración flexible** de todos los períodos desde config.ini

### Próximos Pasos
- Punto 2.3: Implementación de la Lógica de Trading
- Desarrollo de funciones de detección de señales alcistas y bajistas
- Implementación de la máquina de estados para transiciones de señales

## Pila Tecnológica

| Componente | Biblioteca/Framework | Rol Principal |
|------------|---------------------|---------------|
| **Adquisición de Datos** | ccxt | Conexión unificada con APIs de exchanges |
| **Manipulación de Datos** | pandas | Estructuración y manipulación de series temporales |
| **Análisis Técnico** | pandas-ta | Cálculo de indicadores técnicos |
| **Visualización** | mplfinance | Generación de gráficos financieros personalizados |
| **Programación de Tareas** | APScheduler | Orquestación de ejecuciones periódicas |
| **Interfaz de Usuario** | python-telegram-bot | Bot interactivo de Telegram |
| **Gestión de Configuración** | python-dotenv | Carga segura de variables de entorno |

## Estructura del Proyecto

```
proyecto-phoenix/
├── __init__.py
├── main.py                    # Script principal de demostración
├── requirements.txt           # Dependencias del proyecto
├── .env.example              # Plantilla de variables de entorno
├── .gitignore                # Archivos excluidos de git
├── config.ini                # Configuración técnica del sistema
├── core/                     # Núcleo del sistema de análisis
│   ├── __init__.py
│   ├── exchange_connector.py # Conector robusto del exchange
│   ├── analysis_engine.py    # Motor de análisis técnico
│   ├── data_validator.py     # Validador de datos (futuro)
│   └── indicators.py         # Indicadores técnicos (futuro)
├── services/                 # Servicios del sistema
│   ├── __init__.py
│   ├── data_ingestion.py     # Servicio de ingesta (futuro)
│   ├── presentation/         # Servicio de presentación
│   │   ├── __init__.py
│   │   ├── charting_engine.py    # Motor de gráficos (futuro)
│   │   └── ai_payload_formatter.py # Formateador IA (futuro)
│   ├── notification_gateway.py   # Bot de Telegram (futuro)
│   └── scheduler_service.py      # Programador de tareas (futuro)
├── integrations/             # Integraciones externas
│   ├── __init__.py
│   ├── ai_analyzer.py        # Integración con IA (futuro)
│   └── telegram_bot.py       # Bot de Telegram (futuro)
├── utils/                    # Utilidades del sistema
│   ├── __init__.py
│   ├── config_manager.py     # Gestor de configuración
│   ├── logger.py             # Sistema de logging
│   └── exceptions.py         # Excepciones personalizadas
├── tests/                    # Suite de pruebas
│   ├── __init__.py
│   ├── test_exchange_connector.py
│   └── test_analysis_engine.py
└── logs/                     # Directorio de logs
    └── .gitkeep
```

### Directorios Clave

- **`core/`**: Contiene el núcleo computacional del sistema - conector del exchange, motor de análisis y validación de datos
- **`utils/`**: Utilidades transversales como gestión de configuración, logging y excepciones personalizadas  
- **`logs/`**: Almacena los archivos de log rotativos para monitorización y debugging

## Guía de Inicio Rápido

### Prerrequisitos

- **Python 3.10+** (recomendado 3.11 o superior)
- **pip** (gestor de paquetes de Python)
- **git** (para clonación del repositorio)

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/proyecto-phoenix.git
   cd proyecto-phoenix
   ```

2. **Crear y activar entorno virtual**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   # Copiar la plantilla de configuración
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/macOS
   ```
   
   Editar el archivo `.env` con tus credenciales:
   ```bash
   EXCHANGE_ID=binance
   API_KEY=tu_api_key_aqui
   API_SECRET=tu_api_secret_aqui
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   TELEGRAM_CHAT_ID=987654321
   AI_API_KEY=tu_ai_api_key_aqui
   ```

5. **Ejecutar el sistema**
   ```bash
   python main.py
   ```

### Salida Esperada

Al ejecutar correctamente, deberías ver una salida similar a:

```
2025-10-15 22:52:47,498 - phoenix - INFO - === PROYECTO PHOENIX - FASE I: NÚCLEO DE ANÁLISIS ===
2025-10-15 22:52:47,498 - phoenix - INFO - Iniciando integración completa: Conector + Motor de Análisis...
2025-10-15 22:52:47,498 - phoenix - INFO - --- PASO 1: INICIALIZANDO CONECTOR DEL EXCHANGE ---
2025-10-15 22:52:51,676 - phoenix - INFO - Exchange conectado: Binance (binance)
2025-10-15 22:52:51,676 - phoenix - INFO - Obteniendo datos OHLCV para BTC/USDC en 2h
2025-10-15 22:52:51,933 - phoenix - INFO - === DATOS OHLCV OBTENIDOS ===
2025-10-15 22:52:51,934 - phoenix - INFO - Filas obtenidas: 200
2025-10-15 22:52:51,934 - phoenix - INFO - Rango temporal: 2025-09-29 06:00:00 a 2025-10-15 20:00:00
2025-10-15 22:52:51,934 - phoenix - INFO - Precio actual (último cierre): 111314.14
2025-10-15 22:52:51,935 - phoenix - INFO - --- PASO 2: INICIALIZANDO MOTOR DE ANÁLISIS TÉCNICO ---
2025-10-15 22:52:51,935 - phoenix - INFO - Configuración del motor: {'ema_period': 21, 'rsi_period': 14, 'macd_fast': 12, 'macd_slow': 26, 'macd_signal': 9, 'volume_avg_period': 20}
2025-10-15 22:52:51,935 - phoenix - INFO - Calculando indicadores técnicos...
2025-10-15 22:52:51,941 - phoenix - INFO - === DATAFRAME ENRIQUECIDO CON INDICADORES ===
2025-10-15 22:52:51,942 - phoenix - INFO - Columnas totales: 11
2025-10-15 22:52:51,942 - phoenix - INFO - Indicadores añadidos: ['EMA21', 'RSI14', 'MACD', 'MACD_Signal', 'MACD_Histogram', 'Volume_Avg20']
2025-10-15 22:52:51,942 - phoenix - INFO - === VALORES ACTUALES DE INDICADORES ===
2025-10-15 22:52:51,942 - phoenix - INFO - timestamp: 2025-10-15 20:00:00
2025-10-15 22:52:51,943 - phoenix - INFO - close_price: 111314.1400
2025-10-15 22:52:51,943 - phoenix - INFO - ema21: 112267.9253
2025-10-15 22:52:51,943 - phoenix - INFO - rsi14: 39.4834
2025-10-15 22:52:51,943 - phoenix - INFO - macd: -629.9653
2025-10-15 22:52:51,943 - phoenix - INFO - macd_signal: -547.6190
2025-10-15 22:52:51,944 - phoenix - INFO - macd_histogram: -82.3462
2025-10-15 22:52:51,944 - phoenix - INFO - volume: 202.1171
2025-10-15 22:52:51,944 - phoenix - INFO - volume_avg20: 519.9924
2025-10-15 22:52:51,959 - phoenix - INFO - === VERIFICACIÓN DE CALIDAD DE INDICADORES ===
2025-10-15 22:52:51,959 - phoenix - INFO - EMA21: 180/200 valores válidos (90.0%)
2025-10-15 22:52:51,960 - phoenix - INFO - RSI14: 199/200 valores válidos (99.5%)
2025-10-15 22:52:51,960 - phoenix - INFO - MACD: 175/200 valores válidos (87.5%)
2025-10-15 22:52:51,960 - phoenix - INFO - MACD_Signal: 167/200 valores válidos (83.5%)
2025-10-15 22:52:51,960 - phoenix - INFO - MACD_Histogram: 167/200 valores válidos (83.5%)
2025-10-15 22:52:51,961 - phoenix - INFO - Volume_Avg20: 181/200 valores válidos (90.5%)
2025-10-15 22:52:51,961 - phoenix - INFO - ✅ Todos los indicadores tienen valores válidos en las últimas 10 velas
2025-10-15 22:52:51,962 - phoenix - INFO - === INTEGRACIÓN FASE I - COMPLETADA EXITOSAMENTE ===
2025-10-15 22:52:51,962 - phoenix - INFO - ✅ Conector del Exchange: OPERATIVO
2025-10-15 22:52:51,962 - phoenix - INFO - ✅ Motor de Análisis Técnico: OPERATIVO
2025-10-15 22:52:51,962 - phoenix - INFO - ✅ Indicadores calculados: EMA21, RSI14, MACD (3 componentes), Media de Volumen
2025-10-15 22:52:51,962 - phoenix - INFO - 🚀 Sistema listo para la siguiente fase: Lógica de Señales de Trading
```

## Configuración

El sistema utiliza dos archivos de configuración para separar datos sensibles de parámetros técnicos:

### `.env` - Variables de Entorno Sensibles
Contiene credenciales y tokens que **NO deben** ser versionados:
- `EXCHANGE_ID`: ID del exchange (ej: binance, coinbase)
- `API_KEY` / `API_SECRET`: Credenciales del exchange
- `TELEGRAM_BOT_TOKEN`: Token del bot de Telegram
- `TELEGRAM_CHAT_ID`: ID del chat para notificaciones  
- `AI_API_KEY`: Clave para servicios de IA

### `config.ini` - Configuración Técnica
Contiene parámetros técnicos que **SÍ pueden** ser versionados:

```ini
[trading]
pair = BTC/USDC          # Par de trading a analizar
timeframe = 2h           # Temporalidad de las velas

[indicators] 
ema_period = 21          # Período de la EMA
rsi_period = 14          # Período del RSI
macd_fast = 12           # MACD período rápido
macd_slow = 26           # MACD período lento
macd_signal = 9          # MACD período de señal
volume_avg_period = 20   # Período media de volumen

[data]
limit = 200              # Número de velas históricas

[logging]
level = INFO             # Nivel de logging
file = logs/phoenix.log  # Archivo de log
```

## Arquitectura del Sistema

El proyecto sigue un paradigma inspirado en microservicios con los siguientes componentes:

- **Servicio de Ingesta**: Conexión y obtención de datos del exchange
- **Núcleo de Análisis**: Motor computacional con indicadores técnicos  
- **Servicio de Presentación**: Generación de gráficos y formato para IA
- **Pasarela de Notificación**: Bot de Telegram interactivo
- **Servicio de Programación**: Orquestador de tareas periódicas

## Características Técnicas

### ✅ Implementado
- **Conector robusto del exchange** con encapsulación ccxt completa
- **Motor de análisis técnico** con pandas-ta y indicadores configurables
- **Validación crítica de datos** (6 niveles de verificación + integridad de indicadores)
- **Gestión exhaustiva de errores** con reintentos automáticos
- **Sistema de configuración centralizado** y seguro
- **Logging profesional** con rotación automática
- **Calidad de código de producción** (PEP 8, type hints, documentación)

### 🔄 En Desarrollo (Próximas Fases)
- Lógica de señales de trading (detección de patrones alcistas/bajistas)
- Bot de Telegram interactivo con gráficos
- Integración con IA para análisis contextual
- Programador de tareas automático 24/7
- Evolución hacia trading automatizado

## Logs y Monitorización

Los logs se almacenan en `logs/phoenix.log` con rotación automática (10MB máximo, 5 backups). El formato incluye:

- **Timestamp preciso** para trazabilidad
- **Nivel de log** (INFO, WARNING, ERROR)
- **Módulo y función** donde ocurrió el evento
- **Mensaje detallado** del evento

## Licencia

Este proyecto es de uso educativo y de investigación. Ver documentación completa para términos de uso.

---

**Proyecto Phoenix** - Sistema Automatizado de Trading de Criptomonedas  
Desarrollado siguiendo las mejores prácticas de la industria y arquitectura escalable.