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
        # Return empty list instead of hardcoded data
        # In production, this should query the actual database
        return {
            "success": True,
            "products": [],
            "count": 0,
            "message": "No hay productos disponibles. Por favor, contacta con soporte para más información."
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
        # Return error instead of hardcoded inventory data
        # In production, this should query the actual inventory system
        return {
            "success": False,
            "error": "Sistema de inventario no disponible. Por favor, contacta con soporte para verificar disponibilidad.",
            "available": 0,
            "requested": quantity,
            "sufficient": False,
            "product_id": product_id
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
        # Return error instead of hardcoded delivery times
        # In production, this should use geolocation services
        return {
            "success": False,
            "error": "Sistema de cálculo de entrega no disponible. Por favor, contacta con soporte para consultar tiempos de entrega.",
            "address": address,
            "estimated_minutes": 0
        }
    except Exception as e:
        logger.error(f"Error calculating delivery time for {address}: {e}")
        return {
            "estimated_minutes": 0,
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
        # Return empty history instead of hardcoded data
        # In production, this should query the actual customer database
        return {
            "success": True,
            "customer_email": customer_email,
            "orders": [],
            "total_orders": 0,
            "total_spent": 0,
            "message": "No hay historial de pedidos disponible. Por favor, contacta con soporte para más información."
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
