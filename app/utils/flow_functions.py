"""
Example Functions for Professional Flow System
These functions can be used in conversation flows
"""
import re
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_email(email: str) -> Dict[str, Any]:
    """Validate email format"""
    try:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(pattern, email))
        
        return {
            "valid": is_valid,
            "email": email,
            "message": "Email válido" if is_valid else "Email inválido"
        }
    except Exception as e:
        logger.error(f"Error validating email {email}: {e}")
        return {
            "valid": False,
            "email": email,
            "error": str(e)
        }


def calculate_order_total(items: List[Dict[str, Any]], delivery_fee: float = 5.0, tax_rate: float = 0.10) -> Dict[str, Any]:
    """Calculate total order amount"""
    try:
        subtotal = 0.0
        
        for item in items:
            price = float(item.get("price", 0))
            quantity = int(item.get("quantity", 1))
            subtotal += price * quantity
        
        delivery = delivery_fee
        tax = subtotal * tax_rate
        total = subtotal + delivery + tax
        
        return {
            "subtotal": round(subtotal, 2),
            "delivery_fee": round(delivery, 2),
            "tax": round(tax, 2),
            "total": round(total, 2),
            "currency": "USD"
        }
    except Exception as e:
        logger.error(f"Error calculating order total: {e}")
        return {
            "error": str(e),
            "subtotal": 0,
            "delivery_fee": 0,
            "tax": 0,
            "total": 0
        }


def create_order(customer_data: Dict[str, Any], items: List[Dict[str, Any]], total: float) -> Dict[str, Any]:
    """Create order in the system"""
    try:
        # Generate order ID
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create order object
        order = {
            "order_id": order_id,
            "customer": customer_data,
            "items": items,
            "total": total,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "payment_status": "pending"
        }
        
        # Here you would save to database
        # For now, just log it
        logger.info(f"Order created: {order_id}")
        
        return {
            "success": True,
            "order_id": order_id,
            "order": order,
            "message": "Pedido creado exitosamente"
        }
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error al crear el pedido"
        }


def send_order_confirmation(order_id: str, customer_email: str, order_details: Dict[str, Any]) -> Dict[str, Any]:
    """Send order confirmation email"""
    try:
        # Here you would integrate with email service
        # For now, just log it
        logger.info(f"Sending confirmation email to {customer_email} for order {order_id}")
        
        return {
            "success": True,
            "order_id": order_id,
            "email": customer_email,
            "message": "Confirmación enviada exitosamente"
        }
    except Exception as e:
        logger.error(f"Error sending confirmation email: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error al enviar confirmación"
        }


def load_products_from_db() -> Dict[str, Any]:
    """Load products from database"""
    try:
        # Mock products data
        products = [
            {
                "id": "product_1",
                "name": "Café Premium",
                "price": 15.99,
                "description": "Tostado artesanalmente",
                "category": "coffee",
                "active": True
            },
            {
                "id": "product_2",
                "name": "Café Orgánico",
                "price": 18.99,
                "description": "Sin pesticidas",
                "category": "coffee",
                "active": True
            },
            {
                "id": "product_3",
                "name": "Café Especial",
                "price": 22.99,
                "description": "Origen único",
                "category": "coffee",
                "active": True
            }
        ]
        
        return {
            "success": True,
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        logger.error(f"Error loading products: {e}")
        return {
            "success": False,
            "error": str(e),
            "products": [],
            "count": 0
        }


def validate_phone(phone: str) -> Dict[str, Any]:
    """Validate phone number format"""
    try:
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Check if it's a valid length (7-15 digits)
        is_valid = 7 <= len(digits_only) <= 15
        
        return {
            "valid": is_valid,
            "phone": phone,
            "formatted": digits_only,
            "message": "Teléfono válido" if is_valid else "Teléfono inválido"
        }
    except Exception as e:
        logger.error(f"Error validating phone {phone}: {e}")
        return {
            "valid": False,
            "phone": phone,
            "error": str(e)
        }


def check_inventory(product_id: str, quantity: int) -> Dict[str, Any]:
    """Check product inventory"""
    try:
        # Mock inventory check
        inventory = {
            "product_1": 50,
            "product_2": 30,
            "product_3": 20
        }
        
        available = inventory.get(product_id, 0)
        sufficient = available >= quantity
        
        return {
            "available": available,
            "requested": quantity,
            "sufficient": sufficient,
            "product_id": product_id,
            "message": f"Stock disponible: {available}" if sufficient else f"Stock insuficiente. Disponible: {available}"
        }
    except Exception as e:
        logger.error(f"Error checking inventory for {product_id}: {e}")
        return {
            "available": 0,
            "requested": quantity,
            "sufficient": False,
            "product_id": product_id,
            "error": str(e)
        }


def calculate_delivery_time(address: str) -> Dict[str, Any]:
    """Calculate delivery time based on address"""
    try:
        # Mock delivery time calculation
        # In real implementation, this would use geolocation services
        
        delivery_times = {
            "downtown": 30,
            "suburbs": 45,
            "remote": 60
        }
        
        # Simple logic based on address keywords
        address_lower = address.lower()
        if "centro" in address_lower or "downtown" in address_lower:
            estimated_time = delivery_times["downtown"]
        elif "suburb" in address_lower or "residencial" in address_lower:
            estimated_time = delivery_times["suburbs"]
        else:
            estimated_time = delivery_times["remote"]
        
        return {
            "estimated_minutes": estimated_time,
            "address": address,
            "message": f"Tiempo estimado de entrega: {estimated_time} minutos"
        }
    except Exception as e:
        logger.error(f"Error calculating delivery time for {address}: {e}")
        return {
            "estimated_minutes": 60,
            "address": address,
            "error": str(e)
        }


def format_order_summary(order_data: Dict[str, Any]) -> str:
    """Format order summary for display"""
    try:
        customer = order_data.get("customer", {})
        items = order_data.get("items", [])
        total = order_data.get("total", 0)
        
        summary = f"📋 Resumen del Pedido:\n\n"
        summary += f"👤 Cliente: {customer.get('name', 'N/A')}\n"
        summary += f"📧 Email: {customer.get('email', 'N/A')}\n"
        summary += f"📱 Teléfono: {customer.get('phone', 'N/A')}\n\n"
        
        summary += "🛍️ Productos:\n"
        for item in items:
            summary += f"  • {item.get('name', 'N/A')} x{item.get('quantity', 1)} - ${item.get('price', 0)}\n"
        
        summary += f"\n💰 Total: ${total}\n"
        
        return summary
    except Exception as e:
        logger.error(f"Error formatting order summary: {e}")
        return "Error al formatear el resumen del pedido"


def get_customer_history(customer_email: str) -> Dict[str, Any]:
    """Get customer order history"""
    try:
        # Mock customer history
        history = [
            {
                "order_id": "ORD-20240101001",
                "date": "2024-01-01",
                "total": 25.99,
                "status": "delivered"
            },
            {
                "order_id": "ORD-20240115002",
                "date": "2024-01-15",
                "total": 18.99,
                "status": "delivered"
            }
        ]
        
        return {
            "success": True,
            "customer_email": customer_email,
            "orders": history,
            "total_orders": len(history),
            "total_spent": sum(order["total"] for order in history)
        }
    except Exception as e:
        logger.error(f"Error getting customer history for {customer_email}: {e}")
        return {
            "success": False,
            "customer_email": customer_email,
            "error": str(e),
            "orders": [],
            "total_orders": 0,
            "total_spent": 0
        }
