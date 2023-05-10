# code of:
# - send_email_async()
# - send_email_background()
# from https://medium.com/nerd-for-tech/how-to-send-email-using-python-fastapi-947921059f0c
# some changes where made to the code to make it work with the new fastapi-mail version

from fastapi import BackgroundTasks as FastApiBackgroundTasks
from fastapi_mail import FastMail, MessageSchema as FastMailMessageSchema, MessageType as FastMailMessageType

from src.config.setup import settings

# async def send_email_async(subject: str, email_to: str, body: dict):
#     message = FastMailMessageSchema(
#         subject=subject,
#         recipients=[email_to],
#         template_body=body,
#         subtype=FastMailMessageType.html,
#     )

#     fm = FastMail(settings.get_fast_mail_configuration)
#     await fm.send_message(message, template_name='email.html')


def send_email_background(background_tasks: FastApiBackgroundTasks, email_to: str, body: dict):
    message = FastMailMessageSchema(
        subject="GGEA Verification Code",
        recipients=[email_to],
        template_body=body,
        subtype=FastMailMessageType.html,
    )
    fm = FastMail(settings.get_fast_mail_configuration)
    background_tasks.add_task(fm.send_message, message, template_name="verification_email.html")
