import re
import dns.resolver
import smtplib

def check_syntax(email):
    pattern = r'^[a-zA-Z0-9!#$%&\'*+\/=?^_`{|}~-]+(\.[a-zA-Z0-9!#$%&\'*+\/=?^_`{|}~-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,})$'
    if re.match(pattern, email):
        return True
    else:
        return False

def check_mail_server(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        if answers:
            return True
    except dns.resolver.NXDOMAIN:
        pass
    return False

def check_connection(mail_server):
    try:
        with smtplib.SMTP(mail_server) as server:
            return True
    except smtplib.SMTPConnectError:
        pass
    return False

def check_catch_all(email, mail_server):
    try:
        with smtplib.SMTP(mail_server) as server:
            code, _ = server.helo()
            if code == 250:
                code, _ = server.mail('test@example.com')
                if code == 250:
                    code, _ = server.rcpt(email)
                    if code == 250:
                        return False
            return True
    except smtplib.SMTPRecipientsRefused:
        return False

def verify_email(email):
    # Step 1: Check syntax
    if not check_syntax(email):
        return False

    # Extract domain from email
    _, domain = email.split('@')

    # Step 2: Check mail server
    if not check_mail_server(domain):
        return False

    # Step 3: Check connection
    mail_servers = dns.resolver.query(domain, 'MX')
    for mx in mail_servers:
        if check_connection(str(mx.exchange)):
            # Step 4: Check Catch-All
            if check_catch_all(email, str(mx.exchange)):
                return False
            else:
                return True

    return False

# Example usage:
email_address = input("Enter an email address: ")
valid = verify_email(email_address)

if valid:
    print(f"The email address '{email_address}' is valid.")
else:
    print(f"The email address '{email_address}' is not valid.")
