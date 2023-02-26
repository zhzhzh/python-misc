import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename

mail_server = ''


def send_mail(sender: str, to_list: list[str], subject: str, context: str) -> None:
    msg = MIMEText(context, 'html', 'utf-8')
    msg['From'] = sender
    msg['To'] = ','.join(to_list)
    msg['Subject'] = subject

    smtp = smtplib.SMTP()
    smtp.connect(mail_server)
    smtp.sendmail(sender, to_list, msg.as_string())
    smtp.quit()


def send_mail_with_attachments(
    sender: str, to_list: list[str], subject: str, context: str, attachments: list[str]
) -> None:
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ','.join(to_list)
    msg['Subject'] = subject

    msg_text = MIMEText(context, 'html', 'utf-8')
    msg.attach(msg_text)

    for attachment in attachments:
        with open(attachment, 'rb') as file:
            part = MIMEApplication(file.read(), Name=basename(attachment))
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(attachment)
        msg.attach(part)

    smtp = smtplib.SMTP()
    smtp.connect(mail_server)
    smtp.sendmail(sender, to_list, msg.as_string())
    smtp.quit()


def send_mail_with_pngs(
    sender: str, to_list: list[str], subject: str, context: str, png_map: dict[str, str]
) -> None:
    msg = MIMEMultipart('related')
    msg['From'] = sender
    msg['To'] = ','.join(to_list)
    msg['Subject'] = subject

    msg_text = MIMEText(context, 'html', 'utf-8')
    msg.attach(msg_text)

    for png_name in png_map:
        with open(png_map[png_name], 'rb') as image_file:
            msg_image = MIMEImage(image_file.read())
            msg_image.add_header('Content-ID', '<' + png_name + '>')
            msg.attach(msg_image)

    smtp = smtplib.SMTP()
    smtp.connect(mail_server)
    smtp.sendmail(sender, to_list, msg.as_string())
    smtp.quit()
