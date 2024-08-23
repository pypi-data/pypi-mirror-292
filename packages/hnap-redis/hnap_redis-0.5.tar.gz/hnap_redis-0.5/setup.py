from setuptools import setup, find_packages

setup(
    name='hnap_redis',
    version='0.5',
    packages=find_packages(),
    install_requires=[
        # Lista de dependencias, por ejemplo:
        'redis==5.0.7',
    ],
    author='Pablo Padulles',
    author_email='padulles.pablo@hospitalposadas.gob.ar',
    description='Libreria para manejo sencillo de redis',
    #long_description=open('README.md').read(),
    #long_description_content_type='text/markdown',
    url='https://git.hospitalposadas.gob.ar/31258287/hnap_redis',  # URL del repositorio de tu paquete
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
