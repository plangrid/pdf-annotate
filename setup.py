from setuptools import find_packages
from setuptools import setup


setup(
    name='pdf-annotate',
    version='0.11.0',
    description='Add annotations to PDFs',
    author='Michael Bryant',
    author_email='smart-recordset@plangrid.com',
    url='https://github.com/plangrid/pdf-annotate',
    packages=find_packages('.', exclude=['tests*']),
    include_package_data=True,
    install_requires=[
        'attrs>=18.1.0',  # this could probably be lower, but it's not tested
        'pdfrw>=0.4',
        'pillow>=5.2.0',  # this could probably be lower, but it's not tested'
        'fonttools>=3.44.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
