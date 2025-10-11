#!/usr/bin/env python3
"""
Example: Using the new catalog message type
Demonstrates how to use the catalog message functionality
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.whatsapp.message_builder import WhatsAppMessageBuilder, WhatsAppMessageTemplates
from app.services.whatsapp.service import WhatsAppService

async def example_catalog_message():
    """Example of using the new catalog message type"""
    
    # Initialize services
    phone_number = "+5492625661694"  # Test phone number
    builder = WhatsAppMessageBuilder(phone_number)
    templates = WhatsAppMessageTemplates()
    
    print("🔍 Example: Using the new catalog message type")
    print(f"📱 Phone: {phone_number}")
    
    # Example 1: Using the builder directly
    print(f"\n{'='*60}")
    print(f"📦 EXAMPLE 1: Direct Builder Usage")
    print(f"{'='*60}")
    
    # Create product sections (empty for demonstration - no hardcoded data)
    product_sections = [
        builder.create_product_section("Categoría A", []),
        builder.create_product_section("Categoría B", [])
    ]
    
    # Create catalog message with custom texts
    catalog_message = builder.catalog_message(
        catalog_id=os.getenv("WHATSAPP_CATALOG_ID", "785880617687252"),
        product_sections=product_sections,
        header_text="🧊 Catálogo de Productos Congelados",
        body_text="Elegí una opción para ver más detalles 👇",
        footer_text="Productos congelados frescos"
    )
    
    print(f"✅ Catalog message created with builder")
    print(f"📦 Catalog ID: {catalog_message['interactive']['action']['catalog_id']}")
    print(f"📋 Sections: {len(catalog_message['interactive']['action']['sections'])}")
    
    # Example 2: Using templates with custom texts
    print(f"\n{'='*60}")
    print(f"📦 EXAMPLE 2: Template Usage with Custom Texts")
    print(f"{'='*60}")
    
    template_data = templates.native_catalog_message(
        catalog_id=os.getenv("WHATSAPP_CATALOG_ID", "785880617687252"),
        product_sections=[
            {
                "title": "Productos Destacados",
                "product_items": []
            }
        ],
        header_text="🌟 Productos Destacados",
        body_text="Descubre nuestros productos más populares:",
        footer_text="¡No te los pierdas!"
    )
    
    print(f"✅ Catalog template created with custom texts")
    print(f"📦 Type: {template_data['type']}")
    print(f"📦 Catalog ID: {template_data['catalog_id']}")
    print(f"📋 Sections: {len(template_data['product_sections'])}")
    print(f"📝 Header: {template_data['header_text']}")
    
    # Example 3: Using default values
    print(f"\n{'='*60}")
    print(f"📦 EXAMPLE 3: Using Default Values")
    print(f"{'='*60}")
    
    default_template = templates.native_catalog_message(
        catalog_id=os.getenv("WHATSAPP_CATALOG_ID", "785880617687252"),
        product_sections=[
            {
                "title": "Categoría por Defecto",
                "product_items": []
            }
        ]
        # No header_text, body_text, footer_text provided - will use defaults
    )
    
    print(f"✅ Catalog template created with default values")
    print(f"📝 Header (default): {default_template['header_text']}")
    print(f"📝 Body (default): {default_template['body_text']}")
    print(f"📝 Footer (default): {default_template['footer_text']}")
    
    # Example 4: Custom product sections
    print(f"\n{'='*60}")
    print(f"📦 EXAMPLE 4: Custom Product Sections")
    print(f"{'='*60}")
    
    custom_sections = [
        {
            "title": "Categoría A",
            "product_items": []
        },
        {
            "title": "Categoría B",
            "product_items": []
        }
    ]
    
    custom_catalog = builder.catalog_message(
        catalog_id=os.getenv("WHATSAPP_CATALOG_ID", "785880617687252"),
        product_sections=custom_sections,
        header_text="🍽️ Menú del Día",
        body_text="Selecciona tu categoría favorita:",
        footer_text="¡Buen provecho!"
    )
    
    print(f"✅ Custom catalog message created")
    print(f"📦 Header: {custom_catalog['interactive']['header']['text']}")
    print(f"📋 Sections: {len(custom_catalog['interactive']['action']['sections'])}")
    
    # Example 4: Send the message (if WhatsApp service is available)
    print(f"\n{'='*60}")
    print(f"📤 EXAMPLE 4: Sending the Message")
    print(f"{'='*60}")
    
    try:
        whatsapp_service = WhatsAppService()
        
        # Send the catalog message with custom texts
        result = await whatsapp_service.send_message(
            to=phone_number,
            message_type="catalog",
            catalog_id=os.getenv("WHATSAPP_CATALOG_ID", "785880617687252"),
            product_sections=product_sections,
            header_text="🧊 Catálogo de Productos Congelados",
            body_text="Elegí una opción para ver más detalles 👇",
            footer_text="Productos congelados frescos"
        )
        
        if result.get("success"):
            print(f"✅ Catalog message sent successfully!")
            print(f"📨 Message ID: {result.get('message_id')}")
        else:
            print(f"❌ Failed to send catalog message: {result.get('error')}")
            
    except Exception as e:
        print(f"⚠️ WhatsApp service not available: {e}")
        print(f"💡 Message structure is ready for sending")
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Catalog message type added to WhatsAppMessageBuilder")
    print(f"✅ Helper method create_product_section() available")
    print(f"✅ Template native_catalog_message() available")
    print(f"✅ Support for custom headers, body, and footer text")
    print(f"✅ Flexible product sections configuration")
    
    print(f"💡 Usage Examples:")
    print(f"  1. builder.catalog_message(catalog_id, sections)")
    print(f"  2. builder.catalog_message(catalog_id, sections, header='Custom', body='Custom', footer='Custom')")
    print(f"  3. builder.create_product_section(title, product_ids)")
    print(f"  4. templates.native_catalog_message(catalog_id, sections)")
    print(f"  5. templates.native_catalog_message(catalog_id, sections, header='Custom', body='Custom', footer='Custom')")
    print(f"  6. whatsapp_service.send_message(type='catalog', ...)")
    print(f"\n⚠️  IMPORTANT: No hardcoded data - all product data must be provided!")
    print(f"   - Empty sections will show error messages")
    print(f"   - Real product IDs must be provided for production use")
    print(f"   - Header, body, and footer texts are optional with sensible defaults")

if __name__ == "__main__":
    asyncio.run(example_catalog_message())
