from setuptools import setup, find_packages

setup(
    name='mailsafeguard',
    version='0.1.0',
    description='A package to validate and check disposable email addresses',
    author='mohamed thowfick m',
 
    packages=find_packages(),
    install_requires=[
        'requests',
        'dnspython',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
