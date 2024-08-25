from setuptools import setup, find_packages

setup(
    name="fortnite-masteur",  # Remplacez par le nom de votre package
    version="0.1.5",  # La version de votre package
    description="is for manage ftn login and mcp",
    author="the baaguette man",
    author_email="votre.email@example.com",
    url="https://github.com/baguettemanpy",  # URL de votre dépôt GitHub si applicable
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Remplacez par la licence appropriée
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',  # Version minimale de Python requise
)
