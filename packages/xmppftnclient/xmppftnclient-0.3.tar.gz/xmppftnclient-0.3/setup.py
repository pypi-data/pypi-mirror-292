from setuptools import setup, find_packages

setup(
    name='xmppftnclient',            # Nom du module
    version='0.3',                   # Version du module
    packages=find_packages(),        # Trouve automatiquement tous les packages
    install_requires=[
        'aiohttp>=3.8.0',           # Dépendances requises
    ],
    author='Ton Nom',
    author_email='ton.email@example.com',
    description='Client XMPP pour Fortnite via WebSockets',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/toncompte/tonmodule',  # URL du repo si applicable
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)
