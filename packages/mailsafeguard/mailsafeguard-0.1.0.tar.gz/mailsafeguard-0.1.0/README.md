# MailsaFeGuard - Ultimate Email Validation and Filtering Tool 📧🚫

Welcome to **MailsaFeGuard**, the powerful Node.js package designed to ensure the integrity and legitimacy of email addresses. With MailsaFeGuard, you can effortlessly filter out disposable email addresses often used for spam or fraudulent activities. Say goodbye to unreliable email addresses and hello to cleaner, more trustworthy communications! 🌟📩

## Features

### 1. Comprehensive Email Validation 📜✅

- **Syntax Validation**: Ensures that the email format follows standard conventions.
- **Whitelist Check**: Cross-references the email domain with a whitelist of trusted providers like Gmail, Outlook, and Yahoo.
- **Disposable Domain Check**: Compares the domain against a list of known disposable email providers.
- **DNS Resolution**: Verifies the existence and resolution of the email domain via DNS.

### 2. Easy-to-Use Interface 🖥️👌

- Simple and intuitive API for seamless integration into your applications.
- Clear and informative output for each email validation.

### 3. Reliable and Up-to-Date Information 🔄📅

- Regularly updated list of disposable domains from a GitHub repository.
- Robust DNS checks for domain verification.

## How It Works

MailsaFeGuard follows a multi-step approach to ensure email legitimacy:

- **Syntax Validation**: Verifies that the email address adheres to standard formatting rules.
- **Whitelist Check**: Compares the email domain against a list of well-known, trusted email providers.
- **Disposable Domain Check**: Fetches an updated list of disposable email domains from a GitHub repository to check against.
- **DNS Resolution**: Ensures that the domain associated with the email address can be resolved through DNS, including its subdomains.

## Installation

To get started with MailsaFeGuard, install it via npm:

```bash
npm install mailsafeguard


from mailsafeguard.core import is_disposable_email

email = 'test@example.com'
print(is_disposable_email(email))
