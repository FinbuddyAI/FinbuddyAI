from setuptools import setup, find_packages

setup(
    name="finbuddy-ai",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-jose",
        "passlib",
        "python-dotenv",
        "psycopg2-binary",
        "sqlalchemy",
        "openai"
    ],
) 