from setuptools import setup, find_packages
import os

with open('README.md') as f:
    description = f.read()
    
version_file = os.path.join(os.path.dirname(__file__), 'scrapy_cookies', 'VERSION')
with open(version_file, 'r') as f:
    __version__ = f.read().strip()

setup(
    name='scrapy-cookies-fixed',  # Название вашего пакета (оно должно быть уникальным на PyPI)
    version=__version__,  # Версия пакета
    description='A fixed version of scrapy-cookie with updated imports',
    long_description=description,
    long_description_content_type='text/markdown',
    author='aveaxii',
    author_email='kimalex2004dev@gmail.com',

    # packages=['scrapy_cookies'],    
    install_requires=[],  # Укажите зависимости, если есть
    python_requires='>=3.9',  # Укажите минимальную версию Python
)