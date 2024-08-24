from setuptools import setup, find_packages

setup(
    name="xmpp-ftn",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.7.4",
    ],
    author="Votre Nom",
    author_email="votre.email@example.com",
    description="A XMPP connection module for Epic Games services.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/votrecompte/xmpp-module",  # Remplacez par votre dépôt GitHub
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
