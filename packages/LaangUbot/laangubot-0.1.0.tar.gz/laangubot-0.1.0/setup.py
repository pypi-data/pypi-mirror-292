from setuptools import setup, find_packages

setup(
    name="LaangUbot",
    version="0.1.0",
    description="Userbot Hanya Untuk To The Point Aja",
    long_description="Userbot yang dirancang untuk memberikan solusi dengan pendekatan langsung menggunakan Telegram API dan MongoDB.",
    long_description_content_type="text/markdown",
    url="https://github.com/LaangYB/LaangUbot",
    author="LaangYB",
    author_email="your-email@example.com",  # Ganti dengan email Anda
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pyrogram",
        "pymongo",
        "requests",
        # tambahkan dependensi lainnya di sini
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires='>=3.8',
)
