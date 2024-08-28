from setuptools import setup, find_packages
from pathlib import Path

# Чтение содержимого README.md
def read_long_description():
    readme_path = Path(__file__).parent / 'README.md'
    with readme_path.open(encoding='utf-8') as f:
        return f.read()

setup(
    name="blum_crypto",
    version="0.1",
    description="A clicker application for specific images",
    long_description=read_long_description(),
    long_description_content_type='text/markdown',  # Укажите формат содержимого
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "pillow",
        "pyautogui",
        "keyboard"
    ],
    entry_points={
        'console_scripts': [
            'blum-crypto=blum_crypto.main:main',
        ],
    },
    include_package_data=True,
)