from setuptools import setup, find_packages

setup(
    name='mailsafeguard',
    version='0.3.0',
    description='A robust Python package for validating and filtering disposable email addresses to enhance email integrity and security.',
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown',  
    author='thowfickofficial',
    url='https://github.com/thowfickofficial/mailsafeguard',
    project_urls={
        'LinkedIn': 'https://www.linkedin.com/in/thowfickofficial/',
        'Website': 'https://thowfickofficial.netlify.app/',
    },
    packages=find_packages(),
    install_requires=[
        'requests',
        'dnspython',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords=(
        'email validation, disposable email, email filtering, '
        'email security, Python package, email verification, '
        'spam prevention, email integrity, DNS resolution, '
        'email address validation, email protection, cybersecurity, '
        'email checker, email legitimacy, email hygiene, '
        'domain validation, email domain check, email format, '
        'email quality, email verification API, email address checker, '
        'email list management, email validation tool, email address validation tool, '
        'email blacklist, email whitelist, domain verification, '
        'DNS lookup, email fraud prevention, email validation library, '
        'disposable email checker, email validation service, email validation Python, '
        'secure email validation, email validation package, email validation software, '
        'email data quality, email validation script, Python email validation, '
        'email validation algorithm, email domain lookup, email verification tool, '
        'email protection tool, email security tool, email integrity tool'
    ),
    python_requires='>=3.6',
)
