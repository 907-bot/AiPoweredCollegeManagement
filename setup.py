from setuptools import setup, find_packages

setup(
    name="secureexam-pro",
    version="1.0.0",
    description="Enterprise AI-Powered Secure Online Exam & Proctoring Platform",
    author="SecureExam Team",
    author_email="team@secureexam.io",
    python_requires=">=3.11",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "sqlalchemy>=2.0.35",
        "asyncpg>=0.30.0",
        "redis>=5.2.0",
        "pydantic>=2.10.0",
        "pydantic-settings>=2.6.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.17",
        "aiofiles>=24.1.0",
        "httpx>=0.28.0",
        "celery>=5.4.0",
        "opencv-python-headless>=4.10.0",
        "loguru>=0.7.3",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.0",
            "pytest-asyncio>=0.24.0",
        ]
    },
)