import smtplib
import os
from dataclasses import dataclass
from email.message import EmailMessage

from .config import require_env


class NullEmailSender:
    def send(self, subject: str, body: str) -> None:
        return None


@dataclass(frozen=True)
class SMTPEmailSender:
    host: str
    port: int
    username: str
    password: str
    sender: str
    recipient: str
    use_ssl: bool = True

    @classmethod
    def from_env(cls) -> "SMTPEmailSender":
        return cls(
            host=require_env("SMTP_HOST"),
            port=int(require_env("SMTP_PORT")),
            username=require_env("SMTP_USERNAME"),
            password=require_env("SMTP_PASSWORD"),
            sender=require_env("QUESTIONS_EMAIL_FROM"),
            recipient=require_env("QUESTIONS_EMAIL_TO"),
            use_ssl=os.environ.get("SMTP_USE_SSL", "true").lower()
            not in {"0", "false", "no"},
        )

    def send(self, subject: str, body: str) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.sender
        message["To"] = self.recipient
        message.set_content(body)

        if self.use_ssl:
            with smtplib.SMTP_SSL(self.host, self.port) as smtp:
                smtp.login(self.username, self.password)
                smtp.send_message(message)
            return

        with smtplib.SMTP(self.host, self.port) as smtp:
            smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.send_message(message)
