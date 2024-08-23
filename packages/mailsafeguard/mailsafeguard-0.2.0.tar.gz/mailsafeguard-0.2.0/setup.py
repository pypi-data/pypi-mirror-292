from setuptools import setup, find_packages

setup(
    name='mailsafeguard',
    version='0.2.0',
    description='A package to validate and check disposable email addresses',
    long_description=open('README.md').read(),  # Assumes you have a README.md file
    long_description_content_type='text/markdown',  # Markdown format
    author='thowfickofficial',
    url='https://github.com/thowfickofficial/mailsafeguard', 
    packages=find_packages(),
    install_requires=[
        'requests',
        'dnspython',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
