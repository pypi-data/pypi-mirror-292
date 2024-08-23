from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='LibraCreditoPDF1',
    version='0.0.1',
    license='MIT License',
    author='Matheus Nascimento',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='Matheuskater02@outlook.com',
    keywords='leitor all',
    description=u'leitor de PDF extrato',
    packages=['leitor_all'],
    install_requires=['tabula','PyPDF2', 'pandas', 'pdfminer', 'pdfminer.six', 'csv', 'jpype1', 'openpyxl'])