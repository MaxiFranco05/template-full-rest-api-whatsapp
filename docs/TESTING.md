# Guía Completa de Testing - Business API Template

## 📋 Resumen

Esta guía cubre todos los aspectos del sistema de testing del Business API Template, incluyendo tests de WhatsApp, integración API, y flujos conversacionales.

## 🧪 Estructura de Tests

```
tests/
├── README.md                           # Documentación de tests
├── TEST_RESULTS.md                     # Resultados detallados
├── test_real_whatsapp_api.py          # Tests de integración API real
├── test_whatsapp_message_types.py     # Tests de tipos de mensajes nativos
├── test_message_types_flow.json       # Flow JSON para tests
└── unit/
    ├── test_whatsapp_flows_standalone.py    # Tests de flujos standalone
    └── test_professional_flow_system.py     # Tests del sistema de flows
```

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias

```bash
# Instalar requirements de testing
pip install -r requirements-testing.txt

# O instalar dependencias específicas
pip install aiohttp pytest pytest-asyncio python-dotenv
```

### 2. Configurar Variables de Entorno

Asegúrate de tener un archivo `.env` válido con:

```env
# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token
WHATSAPP_API_URL=https://graph.facebook.com/v23.0

# Base de datos
DATABASE_URL=sqlite:///./business_api.db

# Seguridad
SECRET_KEY=your-secret-key
```

## 📱 Tests de Tipos de Mensajes WhatsApp

### Descripción
Test completo que valida todos los tipos de mensajes nativos de WhatsApp Business API.

### Ejecución
```bash
# Con número por defecto
python tests/test_whatsapp_message_types.py

# Con número específico
python tests/test_whatsapp_message_types.py 1234567890
```

### Tipos de Mensajes Probados

#### ✅ Text Messages
- **Tipo**: `text`
- **Estado**: FUNCIONANDO
- **Descripción**: Mensajes de texto simples usando el tipo nativo de WhatsApp

#### ✅ Interactive Messages
- **Tipo**: `interactive`
- **Estado**: FUNCIONANDO
- **Subtipos**:
  - Botones (hasta 3 opciones)
  - Listas desplegables con secciones
- **Características**: Botones de respuesta con IDs personalizados

#### ✅ Media Messages
- **Tipos**: `image`, `document`, `audio`, `video`, `sticker`
- **Estado**: FUNCIONANDO
- **Características**:
  - URLs de medios públicos
  - Captions opcionales
  - Reproductores automáticos

#### ✅ Location Messages
- **Tipo**: `location`
- **Estado**: FUNCIONANDO
- **Características**: Coordenadas GPS, nombres, direcciones

#### ✅ Contact Messages
- **Tipo**: `contacts`
- **Estado**: FUNCIONANDO
- **Características**: Tarjetas de contacto completas

#### ⚠️ Template Messages
- **Tipo**: `template`
- **Estado**: FALLA (Esperado)
- **Razón**: Requieren aprobación previa de Meta
- **Error**: Template name does not exist in the translation

### Resultados
- **Pasos Exitosos**: 13/14
- **Tasa de Éxito**: 92.9%
- **Tiempo de Ejecución**: ~45 segundos

## 🔗 Tests de Integración API

### Descripción
Tests que validan la integración completa con la API real de WhatsApp.

### Ejecución
```bash
python tests/test_real_whatsapp_api.py 1234567890
```

### Funcionalidades Probadas
- Envío de mensajes simples
- Inicio de conversaciones con flows
- Validación de credenciales
- Manejo de errores de API

## 🔄 Tests de Flujos Conversacionales

### Descripción
Tests que validan el sistema de flujos conversacionales sin dependencias externas.

### Ejecución
```bash
python tests/unit/test_whatsapp_flows_standalone.py
```

### Funcionalidades Probadas
- Carga de flows desde JSON/YAML
- Ejecución de flows con servicios mock
- Manejo de estados de conversación
- Validación de pasos de flow

## 📊 Métricas y Resultados

### Resumen General
- **Tests Totales**: 4 suites principales
- **Cobertura**: Todos los tipos de mensajes WhatsApp
- **Tasa de Éxito**: 92.9% (13/14 tipos de mensajes)
- **Tiempo Total**: ~2 minutos para suite completa

### Detalles por Test

| Test | Estado | Éxito | Tiempo | Notas |
|------|--------|-------|--------|-------|
| Tipos de Mensajes | ✅ | 13/14 | 45s | Template falla (esperado) |
| Integración API | ✅ | 100% | 30s | Requiere credenciales |
| Flujos Standalone | ✅ | 100% | 15s | Sin dependencias |
| Sistema de Flows | ✅ | 100% | 20s | Tests unitarios |

## 🛠️ Troubleshooting

### Problemas Comunes

#### 1. Error de Credenciales
```
ERROR: WHATSAPP_ACCESS_TOKEN is not set
```
**Solución**: Verificar archivo `.env` y credenciales de WhatsApp

#### 2. Error de Unicode
```
UnicodeEncodeError: 'charmap' codec can't encode character
```
**Solución**: Los tests están configurados para evitar emojis en Windows

#### 3. Error de Dependencias
```
ModuleNotFoundError: No module named 'aiohttp'
```
**Solución**: Instalar requirements de testing
```bash
pip install -r requirements-testing.txt
```

#### 4. Error de Template
```
Template name does not exist in the translation
```
**Solución**: Este error es esperado - los templates requieren aprobación de Meta

### Logs de Debug

Los tests incluyen logs detallados para debugging:

```bash
# Ejecutar con logs detallados
python tests/test_whatsapp_message_types.py 1234567890 2>&1 | tee test_output.log
```

## 📈 Mejoras Futuras

### Implementaciones Pendientes
1. **Métodos en WhatsAppService**: Agregar métodos específicos para cada tipo de mensaje
2. **Templates Aprobados**: Obtener templates aprobados de Meta para tests completos
3. **Tests de Performance**: Medir tiempos de respuesta de API
4. **Tests de Carga**: Validar comportamiento bajo carga

### Optimizaciones
1. **Paralelización**: Ejecutar tests en paralelo
2. **Caching**: Cachear respuestas de API para tests repetitivos
3. **Mocking**: Usar mocks para tests más rápidos
4. **CI/CD**: Integrar con pipelines de CI/CD

## 📚 Referencias

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [pytest Documentation](https://docs.pytest.org/)
- [aiohttp Documentation](https://docs.aiohttp.org/)

## 🤝 Contribución

Para contribuir a los tests:

1. Fork el repositorio
2. Crear branch para nueva funcionalidad
3. Agregar tests correspondientes
4. Ejecutar suite completa
5. Crear Pull Request

### Estándares de Testing
- Nombres descriptivos para tests
- Documentación clara de propósito
- Manejo de errores robusto
- Logs informativos
- Resultados medibles
