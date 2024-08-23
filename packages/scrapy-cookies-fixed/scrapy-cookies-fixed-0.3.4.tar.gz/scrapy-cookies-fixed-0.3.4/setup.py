from setuptools import setup, find_packages

with open('README.md') as f:
    description = f.read()

setup(
    name='scrapy-cookies-fixed',  # Название вашего пакета (оно должно быть уникальным на PyPI)
    version='0.3.4',  # Версия пакета
    description='A fixed version of scrapy-cookie with updated imports',
    long_description=description,
    long_description_content_type='text/markdown',
    author='aveaxii',
    author_email='kimalex2004dev@gmail.com',
    url='https://github.com/aveaxii',
    packages=['scrapy_cookies'],    
    install_requires=[],  # Укажите зависимости, если есть
    python_requires='>=3.9',  # Укажите минимальную версию Python
)