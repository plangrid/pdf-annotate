from setuptools import find_packages
from setuptools import setup


setup(
    name='pdf-annotate',
    version='0.0.1',
    description='Add annotations to PDFs',
    author='Michael Bryant',
    author_email='smart-recordset@plangrid.com',
    url='https://github.com/plangrid/pdf-annotate',
    packages=find_packages('.'),
    install_requires=[
        'pdfrw>=0.4',
    ],
)
