from setuptools import setup, find_packages
import os

# Cek apakah README.md ada dan bisa dibaca
readme_file = "README.md"
if os.path.exists(readme_file):
    with open(readme_file, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "A short description of your project"

setup(
    name="pyLaang",  # Nama proyek Anda
    version="0.1.0",  # Versi proyek
    author="LaangYB",  # Nama Anda
    author_email="sedekgaming123@gmail.com",  # Email Anda
    description="bot ini dibuat untuk to the point",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LaangYB/LaangUbot",  # URL repositori proyek
    packages=find_packages(),  # Menemukan dan menyertakan semua paket secara otomatis
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Versi minimum Python
    install_requires=[
        # Daftar dependensi di sini
        "requests",
        "numpy",
    ],
)
