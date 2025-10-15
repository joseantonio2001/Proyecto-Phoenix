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

✅ **Fase I - Punto 2.3: Implementación de la Lógica de Trading - COMPLETADO**

El sistema ahora puede generar señales de trading (BULLISH_SIGNAL, BEARISH_SIGNAL, NO_SIGNAL) utilizando una lógica "stateful" avanzada:

- **Detección inteligente de eventos**: Análisis de transición entre la vela anterior y actual para identificar cambios de estado
- **Lógica stateful**: Diferenciación entre "estado" y "evento" para evitar alertas redundantes
- **Reglas de señales precisas**: Implementación exacta de condiciones alcistas/bajistas basadas en EMA, RSI, MACD e indicadores de volumen
- **Análisis de dos velas**: Comparación sistemática entre vela actual (iloc[-1]) y anterior (iloc[-2])
- **Prevención de spam**: Las señales solo se generan cuando las condiciones pasan de NO cumplidas a SÍ cumplidas
- **Estados claros y definidos**: Salida única y explícita del resultado del análisis

🎯 **FASE I - NÚCLEO DE ANÁLISIS: COMPLETADA EXITOSAMENTE**

El núcleo de análisis es ahora una unidad funcional, robusta y completa que proporciona la base computacional para todas las fases posteriores del proyecto.

### Próximos Pasos
- **Fase II - La Interfaz de Usuario: Visualización e Interacción**
- Punto 3.1: Motor de Gráficos Financieros con mplfinance
- Desarrollo de visualización profesional de datos y señales
- Integración de capacidades de exportación y personalización de gráficos

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
│   ├── trading_signals.py    # Motor de señales de trading
│   ├── data_validator.py     # Validador de datos (futuro)
│   └── indicators.py         # Indicadores técnicos (futuro)
├── services/                 # Servicios del sistema
│   ├── __init__.py
│   ├── data_ingestion.py     # Servicio de ingesta (futuro)
│   ├── presentation/         # Servicio de presentación
│   │   ├── __init__.py
│   │   ├── charting_engine.py    # Motor de gráficos (próximo)
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
│   ├── test_analysis_engine.py
│   └── test_trading_signals.py
└── logs/                     # Directorio de logs
    └── .gitkeep
```

### Directorios Clave

- **`core/`**: Contiene el núcleo computacional completo del sistema - conector del exchange, motor de análisis técnico y motor de señales de trading
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
   git clone https://github.com/joseantonio2001/proyecto-phoenix.git
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
2025-10-16 00:41:27,659 - phoenix - INFO - === PROYECTO PHOENIX - FASE I: NÚCLEO DE ANÁLISIS COMPLETO ===
2025-10-16 00:41:27,659 - phoenix - INFO - Iniciando pipeline completo: Conector → Análisis → Señales...
2025-10-16 00:41:27,659 - phoenix - INFO - --- PASO 1: INICIALIZANDO CONECTOR DEL EXCHANGE ---
2025-10-16 00:41:32,903 - phoenix - INFO - Exchange conectado: Binance (binance)
2025-10-16 00:41:32,903 - phoenix - INFO - Obteniendo datos OHLCV para BTC/USDC en 2h
2025-10-16 00:41:33,160 - phoenix - INFO - === DATOS OHLCV OBTENIDOS ===
2025-10-16 00:41:33,161 - phoenix - INFO - Filas obtenidas: 200
2025-10-16 00:41:33,161 - phoenix - INFO - Rango temporal: 2025-09-29 08:00:00 a 2025-10-15 22:00:00
2025-10-16 00:41:33,161 - phoenix - INFO - Precio actual (último cierre): 111332.40
2025-10-16 00:41:33,161 - phoenix - INFO - --- PASO 2: INICIALIZANDO MOTOR DE ANÁLISIS TÉCNICO ---
2025-10-16 00:41:33,162 - phoenix - INFO - Configuración del motor: {'ema_period': 21, 'rsi_period': 14, 'macd_fast': 12, 'macd_slow': 26, 'macd_signal': 9, 'volume_avg_period': 20}
2025-10-16 00:41:33,162 - phoenix - INFO - Calculando indicadores técnicos...
2025-10-16 00:41:33,168 - phoenix - INFO - === DATAFRAME ENRIQUECIDO CON INDICADORES ===
2025-10-16 00:41:33,168 - phoenix - INFO - Columnas totales: 11
2025-10-16 00:41:33,169 - phoenix - INFO - Indicadores añadidos: ['EMA21', 'RSI14', 'MACD', 'MACD_Signal', 'MACD_Histogram', 'Volume_Avg20']
2025-10-16 00:41:33,169 - phoenix - INFO - --- PASO 3: INICIALIZANDO MOTOR DE SEÑALES DE TRADING ---
2025-10-16 00:41:33,169 - phoenix - INFO - Analizando señales de trading con lógica stateful...
2025-10-16 00:41:33,170 - phoenix - INFO - === ANÁLISIS DE SEÑALES COMPLETADO ===
2025-10-16 00:41:33,170 - phoenix - INFO - === RESULTADO DE LA DETECCIÓN DE SEÑALES ===
2025-10-16 00:41:33,171 - phoenix - INFO - 
⚪ SIN SEÑAL RELEVANTE:
• Precio $111,332.40 vs EMA21 $112,148.96 (BELOW)
• RSI 41.2 en zona NEUTRAL_BEARISH
• MACD Histograma NEGATIVE (-75.92)
• Volumen LOW (ratio: 0.18x)
• No se detectó transición en las condiciones de entrada
2025-10-16 00:41:33,171 - phoenix - INFO - === DETALLES TÉCNICOS DEL ANÁLISIS ===
2025-10-16 00:41:33,171 - phoenix - INFO - ⚪ SIN SEÑAL RELEVANTE EN EL CICLO ACTUAL
2025-10-16 00:41:33,171 - phoenix - INFO - Razón: No se detectó transición de estado en las condiciones de entrada
2025-10-16 00:41:33,171 - phoenix - INFO - Estado actual de condiciones alcistas:
2025-10-16 00:41:33,172 - phoenix - INFO -   ❌ price_above_ema
2025-10-16 00:41:33,172 - phoenix - INFO -   ✅ rsi_in_range
2025-10-16 00:41:33,172 - phoenix - INFO -   ❌ macd_histogram_positive
2025-10-16 00:41:33,172 - phoenix - INFO -   ❌ volume_above_average
2025-10-16 00:41:33,172 - phoenix - INFO - Estado actual de condiciones bajistas:
2025-10-16 00:41:33,172 - phoenix - INFO -   ✅ price_below_ema
2025-10-16 00:41:33,172 - phoenix - INFO -   ❌ rsi_in_range
2025-10-16 00:41:33,173 - phoenix - INFO -   ✅ macd_histogram_negative
2025-10-16 00:41:33,173 - phoenix - INFO -   ❌ volume_above_average
2025-10-16 00:41:33,173 - phoenix - INFO - === VALORES DE INDICADORES EN VELA ACTUAL ===
2025-10-16 00:41:33,173 - phoenix - INFO - Timestamp: 2025-10-15 22:00:00
2025-10-16 00:41:33,173 - phoenix - INFO - Precio actual: $111,332.40
2025-10-16 00:41:33,173 - phoenix - INFO - EMA21: $112,148.96 (BELOW)
2025-10-16 00:41:33,173 - phoenix - INFO - RSI14: 41.16 (NEUTRAL_BEARISH)
2025-10-16 00:41:33,173 - phoenix - INFO - MACD Histograma: -75.9243 (NEGATIVE)
2025-10-16 00:41:33,174 - phoenix - INFO - Volumen: 0.18x promedio (LOW)
2025-10-16 00:41:33,174 - phoenix - INFO - === ANÁLISIS DE TRANSICIÓN ENTRE VELAS ===
2025-10-16 00:41:33,174 - phoenix - INFO - No se detectó transición válida:
2025-10-16 00:41:33,174 - phoenix - INFO - • Las condiciones pueden estar cumplidas en ambas velas (sin evento)
2025-10-16 00:41:33,174 - phoenix - INFO - • O las condiciones no están completamente cumplidas en la vela actual
2025-10-16 00:41:33,174 - phoenix - INFO - • La lógica stateful evita alertas redundantes
2025-10-16 00:41:33,174 - phoenix - INFO - === FASE I - NÚCLEO DE ANÁLISIS: COMPLETADO EXITOSAMENTE ===
2025-10-16 00:41:33,174 - phoenix - INFO - ✅ Conector del Exchange: OPERATIVO
2025-10-16 00:41:33,174 - phoenix - INFO - ✅ Motor de Análisis Técnico: OPERATIVO
2025-10-16 00:41:33,174 - phoenix - INFO - ✅ Motor de Señales de Trading: OPERATIVO
2025-10-16 00:41:33,174 - phoenix - INFO - ✅ Lógica Stateful: Diferenciación entre estado y evento implementada
2025-10-16 00:41:33,175 - phoenix - INFO - 🎯 Resultado final del ciclo: NO_SIGNAL
2025-10-16 00:41:33,175 - phoenix - INFO - 🚀 Sistema listo para la siguiente fase: Interfaz de Usuario y Bot de Telegram
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
- **Núcleo de Análisis**: Motor computacional con indicadores técnicos y señales de trading  
- **Servicio de Presentación**: Generación de gráficos y formato para IA
- **Pasarela de Notificación**: Bot de Telegram interactivo
- **Servicio de Programación**: Orquestador de tareas periódicas

## Características Técnicas

### ✅ Implementado
- **Conector robusto del exchange** con encapsulación ccxt completa
- **Motor de análisis técnico** con pandas-ta y indicadores configurables
- **Motor de señales de trading** con lógica stateful para detección inteligente de eventos
- **Validación crítica de datos** (6 niveles de verificación + integridad de indicadores)
- **Gestión exhaustiva de errores** con reintentos automáticos
- **Sistema de configuración centralizado** y seguro
- **Logging profesional** con rotación automática
- **Calidad de código de producción** (PEP 8, type hints, documentación)

### 🔄 En Desarrollo (Próximas Fases)
- Motor de gráficos financieros con mplfinance (Fase II - Punto 3.1)
- Bot de Telegram interactivo con visualizaciones
- Integración con IA para análisis contextual
- Programador de tareas automático 24/7
- Evolución hacia trading automatizado

## Pipeline de Procesamiento

El sistema implementa un pipeline completo de procesamiento de datos financieros:

1. **Ingesta de Datos**: Obtención robusta de datos OHLCV del exchange
2. **Enriquecimiento**: Cálculo de indicadores técnicos con pandas-ta
3. **Análisis de Señales**: Detección inteligente de patrones de trading
4. **Evaluación Stateful**: Diferenciación entre estado y evento para prevenir spam
5. **Resultado Final**: Generación de señal clara (BULLISH_SIGNAL, BEARISH_SIGNAL, NO_SIGNAL)

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