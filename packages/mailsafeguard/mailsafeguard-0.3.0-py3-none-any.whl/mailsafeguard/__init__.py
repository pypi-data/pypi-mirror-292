import requests
import dns.resolver
import re

GITHUB_JSON_URL = 'https://raw.githubusercontent.com/thowfickofficial/disposable-email-domains-list/master/disposable-email-domains-list.json'

WHITELIST = [
    'gmail.com',
    'outlook.com',
    'yahoo.com',
    'hotmail.com',
    'icloud.com',
    'aol.com',
    'live.com',
    'protonmail.com',
    'me.com',
    'msn.com',
    'yandex.com',
    'mail.com'
]

def is_valid_json_array(data):
    return isinstance(data, list) and all(isinstance(item, str) for item in data)

def fetch_disposable_email_domains():
    try:
        response = requests.get(GITHUB_JSON_URL)
        response.raise_for_status()
        domains = response.json()
        if is_valid_json_array(domains):
            return domains
        else:
            raise ValueError('Invalid JSON structure.')
    except Exception as e:
        raise RuntimeError(f'Failed to fetch data: {e}')

def is_valid_email_syntax(email):
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(email_regex, email) is not None

def check_dns_resolution(domain):
    try:
        dns.resolver.resolve(domain, 'A')
        print(f'DNS resolution succeeded for domain: {domain}')
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        print(f'DNS resolution failed for domain: {domain}')
        return False

def check_dns_for_domain_and_subdomains(domain):
    parts = domain.split('.')
    while len(parts) > 2:
        current_domain = '.'.join(parts)
        if check_dns_resolution(current_domain):
            return True
        parts.pop(0)
    return check_dns_resolution('.'.join(parts))

def is_disposable_email(email):
    try:
        if not is_valid_email_syntax(email):
            print('Invalid email syntax.')
            return True

        email_domain = email.split('@')[1].lower()
        domain_parts = email_domain.split('.')

        if len(domain_parts) > 15:
            print(f'Domain has more than 15 subdomain parts: {email_domain}')
            return True

        if email_domain in WHITELIST:
            print(f'Domain is whitelisted: {email_domain}')
            return False

        disposable_email_domains = fetch_disposable_email_domains()

        if email_domain in disposable_email_domains:
            print(f'Domain found in disposable list: {email_domain}')
            return True

        dns_resolved = check_dns_for_domain_and_subdomains(email_domain)
        if not dns_resolved:
            print(f'Domain does not resolve: {email_domain}')
            return True

        return False

    except Exception as e:
        print(f'Error: {e}')
        return True
