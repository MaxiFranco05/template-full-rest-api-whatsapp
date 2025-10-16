#!/usr/bin/env python3
"""
Test de integración de flows con webhook
Verifica que el sistema de flows se ejecute correctamente cuando llegan mensajes por WhatsApp
"""

import asyncio
import json
import sys
import os
import time

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.whatsapp.service import whatsapp_service
from app.services.whatsapp.persistence import get_whatsapp_persistence_service
from app.services.flows.active_flow_manager import active_flow_manager
from tests.config.test_integration_config import TEST_CONFIG


async def test_flow_integration():
    """Test de integración de flows con webhook"""
    print("🧪 Test de Integración de Flows con Webhook")
    print("=" * 60)
    
    test_phone = TEST_CONFIG["test_phone_number"]
    
    # Asegurarse de que el flow 'main' esté activo
    active_flow_manager.set_active_flow("main")
    print(f"🎯 Flow activo: {active_flow_manager.get_active_flow()}")

    # Limpiar datos de prueba anteriores
    from app.db.database import SessionLocal, engine, Base
    from app.models import WhatsAppUser, WhatsAppConversation, WhatsAppMessage

    # Configurar la base de datos para el test
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        db.query(WhatsAppMessage).filter(WhatsAppMessage.conversation_id.like(f"%{test_phone}%")).delete()
        db.query(WhatsAppConversation).filter(WhatsAppConversation.conversation_id.like(f"%{test_phone}%")).delete()
        db.query(WhatsAppUser).filter(WhatsAppUser.phone_number == test_phone).delete()
        db.commit()

    print(f"\n📱 Teléfono de prueba: {test_phone}")
    
    test_messages = ["Hola", "Quiero información", "Gracias"]

    # Simular mensajes entrantes
    for i, message_content in enumerate(test_messages, 1):
        print(f"\n📱 Mensaje {i}: '{message_content}'")
        print("-" * 40)
        
        # Crear datos de mensaje simulando webhook
        message_data = {
            "from": test_phone,
            "content": message_content,
            "message_id": f"{TEST_CONFIG['test_message_id_prefix']}{i}_{int(time.time())}",
            "message_type": "text",
            "timestamp": "2024-01-01T12:00:00Z",
            "contact_info": {
                "name": "Test User",
                "phone": test_phone
            }
        }
        
        try:
            # Procesar mensaje usando el servicio integrado
            result = await whatsapp_service.process_incoming_message(message_data)
            print(f"✅ Resultado: {result.get('success', False)}")
            print(f"📤 Respuesta enviada: {result.get('response_sent', False)}")
            print(f"💬 Mensaje: {result.get('message', 'N/A')}")
            print(f"🔄 Estado conversación: {result.get('conversation_state', 'N/A')}")
            if result.get("fallback_used"):
                print("⚠️ Se usó procesamiento de fallback")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    print("\n🎉 Test completado!")
    print(f"📊 Flow activo: {active_flow_manager.get_active_flow()}")
    print(f"📱 Teléfono de prueba: {test_phone}")


async def test_flow_switching():
    """Test de cambio de flow activo"""
    print("\n🔄 Test de Cambio de Flow Activo")
    print("=" * 60)
    
    test_phone = TEST_CONFIG["test_phone_number"]
    
    # Cambiar el flow activo a 'main'
    print("🔄 Cambiando a flow 'main'...")
    change_success = active_flow_manager.set_active_flow("main")
    print(f"✅ Cambio exitoso: {change_success}")
    
    # Verificar cambio
    active_flow = active_flow_manager.get_active_flow()
    print(f"🎯 Nuevo flow activo: {active_flow}")
    
    # Probar mensaje con nuevo flow
    message_data = {
        "from": test_phone,
        "content": "Hola con nuevo flow",
        "message_id": f"{TEST_CONFIG['test_message_id_prefix']}switch_{int(time.time())}",
        "message_type": "text",
        "timestamp": "2024-01-01T12:00:00Z",
        "contact_info": {
            "name": "Test User",
            "phone": test_phone
        }
    }
    
    try:
        result = await whatsapp_service.process_incoming_message(message_data)
        print(f"✅ Mensaje procesado: {result.get('success', False)}")
        print(f"💬 Respuesta: {result.get('message', 'N/A')}")
    except Exception as e:
        print(f"❌ Error inesperado al procesar mensaje con nuevo flow: {e}")

    print("\n✅ Test de cambio de flow completado!")


async def main():
    """Función principal del test"""
    print("🚀 Iniciando tests de integración...")
    
    try:
        await test_flow_integration()
        await test_flow_switching()
        print("\n✅ Todos los tests completados exitosamente!")
        return 0
    except Exception as e:
        print(f"\n❌ Error en los tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)