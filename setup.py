from setuptools import setup, find_packages

setup(
    name="feedback-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pymongo",
        "python-dotenv",
        "certifi"
    ],
    python_requires=">=3.8",
) 