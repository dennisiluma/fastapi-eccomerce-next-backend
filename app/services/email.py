from email.message import EmailMessage
from pathlib import Path

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.core.exceptions import ApiException
from app.models.order import Order

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


async def send_welcome_email(email: str, name: str):
    print("Inside send_welcome_email")

    print(f"Mail Host: {settings.MAIL_HOST}")

    # SETUP UP OUR EMAIL INSTANCE
    message = EmailMessage()
    message["Subject"] = "Welcome to ShopEase"
    message["from"] = settings.MAIL_FROM
    message["to"] = email

    # render & BUILD the HTML template (welcome.html)
    try:
        template = jinja_env.get_template("welcome.html")
        html_content = template.render(name=name, frontendUrl=settings.FRONTEND_URL)
        message.add_alternative(html_content, subtype="html")
    except Exception as e:
        message.set_content(f"Hello {name}, welcome to ShopEase")
        print(f"⚠️ Template Error: {e}")

    # NOW SENDING THE EMAIL OUR
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_HOST,
            port=int(settings.MAIL_PORT),
            username=settings.MAIL_USER,
            password=settings.MAIL_PASS,
        )
        print("welcoem email sent succesfully")

    except Exception as e:
        print(f"Error sending welcome eamil out: {e}")
        raise ApiException(
            message=f"Error sending email {e}",
            status_code=500,
        )


async def send_reset_password_email(email: str, name: str, code: str, reset_url: str):
    print("Inside send_reset_password_email")

    # SETUP UP OUR EMAIL INSTANCE
    message = EmailMessage()
    message["Subject"] = "Password Reset Request - Action Required"
    message["from"] = settings.MAIL_FROM
    message["to"] = email

    # render & BUILD the HTML template (welcome.html)
    try:
        template = jinja_env.get_template("reset-password.html")
        html_content = template.render(name=name, code=code, reset_url=reset_url)
        message.add_alternative(html_content, subtype="html")

    except Exception as e:
        # Fallback text
        message.set_content(
            f"Hello {name}, your reset code is: {code}. Link: {reset_url}"
        )
        print(f"⚠️ Template Error: {e}")

    # NOW SENDING THE EMAIL OUR
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_HOST,
            port=int(settings.MAIL_PORT),
            username=settings.MAIL_USER,
            password=settings.MAIL_PASS,
        )
        print("Forgot Password email sent succesfully")

    except Exception as e:
        print(f"Error sending Forgot Password email out: {e}")

        raise ApiException(
            message=f"Error sending email {e}",
            status_code=500,
        )


async def send_order_status_update_email(email: str, name: str, order: Order):
    try:
        template = jinja_env.get_template("order-status.html")

        # We pass the order items directly to the template
        html_content = template.render(
            name=name,
            order_id=order.id,
            status=order.status.value.upper(),
            address=order.shipping_address,
            total_price=order.total_price,
            items=order.items,  # Passing the list of OrderItem objects
        )

        message = EmailMessage()
        message["Subject"] = f"Update: Order #{order.id} is now {order.status.value}"
        message["From"] = settings.MAIL_FROM
        message["To"] = email
        message.add_alternative(html_content, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_HOST,
            port=int(settings.MAIL_PORT),
            username=settings.MAIL_USER,
            password=settings.MAIL_PASS,
            start_tls=True,
        )

        print("ORDER status updated sent succesfully")

    except Exception as e:
        print(f"❌ Email Error: {e}")




async def send_order_confirmation_email(email: str, name: str, order: Order):

    template = jinja_env.get_template("order_confirmation.html")
    html_content = template.render(
        name=name,
        order_id=order.id,
        total=order.total_price,
        address=order.shipping_address,
    )

    message = EmailMessage()
    message["Subject"] = f"Confirmation: Order #{order.id}"
    message["From"] = settings.MAIL_FROM
    message["To"] = email
    message.add_alternative(html_content, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_HOST,
            port=int(settings.MAIL_PORT),
            username=settings.MAIL_USER,
            password=settings.MAIL_PASS,
            start_tls=True,
        )
        print(f"✅ Order Confirmation email sent to {email}")
    except Exception as e:
        print(f"❌ SMTP Error for sending Order Confirmation email: {e}")




async def notify_delivery_team_of_order(order:Order, customer_name:str):

    try:
        template = jinja_env.get_template("delivery_person_order_notification.html")

        html_content = template.render(
            customer_name=customer_name,
            order_id=order.id,
            order_status=order.status,
            payment_status=order.payment.status if order.payment else "Unknown",
            total=order.total_price,
            address=order.shipping_address,
            items=order.items,  # This allows the admin to see the product list
            order_date=order.created_at.strftime("%Y-%m-%d %H:%M"),
        )

        message = EmailMessage()
        message["Subject"] = f"🚨 New Order Received: #{order.id}"
        message["From"] = settings.MAIL_FROM
        message["To"] = settings.DELIVERY_PERSON_EMAIL  # Ensure this is in your delibery email
        message.add_alternative(html_content, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_HOST,
            port=int(settings.MAIL_PORT),
            username=settings.MAIL_USER,
            password=settings.MAIL_PASS,
            start_tls=True,
        )
        print(f"✅ Delivery team notified of Order #{order.id}")
    except Exception as e:
        print(f"❌ Delivery Email Error to notify Delivery Man: {e}")





async def send_payment_notification(
    email: str,
    name: str,
    order_id: int,
    status: str,
    amount: str = None,
    error: str = None,  
):
    template_name = (
        "payment-success.html" if status == "success" else "payment-failed.html"
    )
    subject = (
        f"Payment Successful - Order #{order_id}"
        if status == "success"
        else f"Payment Failed - Order #{order_id}"
    )


    try:
        template = jinja_env.get_template(template_name)
        html_content = template.render(
            name=name,
            order_id=order_id,
            amount=amount,
            currency="USD",
            error_message=error,
        )

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.MAIL_FROM
        message["To"] = email
        message.add_alternative(html_content, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_HOST,
            port=int(settings.MAIL_PORT),
            username=settings.MAIL_USER,
            password=settings.MAIL_PASS,
            start_tls=True,
        )
        print("success sending payment email out")
        
    except Exception as e:
        print(f"❌ Email error: {e}")
    