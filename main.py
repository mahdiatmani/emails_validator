import re
import dns.resolver
import smtplib
i= 1
color_red = "\033[31m"
color_green = "\033[32m"

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
    # Remove trailing dot (".") if present
    email = email.rstrip('.')

    # Step 1: Check syntax
    if not check_syntax(email):
        return False

    # Extract domain from email
    _, domain = email.split('@')

    # Step 2: Check mail server
    if not check_mail_server(domain):
        return False

    # Step 3: Check connection
    mail_servers = dns.resolver.resolve(domain, 'MX')
    for mx in mail_servers:
        if check_connection(str(mx.exchange)):
            # Step 4: Check Catch-All
            if check_catch_all(email, str(mx.exchange)):
                return False
            else:
                return True

    return False

# Example usage:
filename = "emails.txt"
valid_emails_file = "valid_emails.txt"
invalid_emails_file = "invalid_emails.txt"

with open(filename, 'r') as file, open(valid_emails_file, 'w') as valid_file, open(invalid_emails_file, 'w') as invalid_file:
    for line in file:
        email_address = line.strip()
        valid = verify_email(email_address)
        if valid:
            valid_file.write(email_address + '\n')
            print(color_green + email_address)
        else:
            invalid_file.write(email_address + '\n')
            print(color_red + email_address)

print("Validation completed. Valid email addresses saved in 'valid_emails.txt'. Invalid email addresses saved in 'invalid_emails.txt'.")
