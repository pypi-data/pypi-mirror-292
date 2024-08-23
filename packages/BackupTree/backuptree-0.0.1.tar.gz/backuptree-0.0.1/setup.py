from setuptools import setup, find_packages

setup(
    name='BackupTree',
    version='0.0.1',
    author='Maycon Cypriano Batestin',
    author_email='mayconcipriano@gmail.com',
    packages=find_packages(),  # Isso procura e inclui todos os pacotes no diretório atual.
    include_package_data=True,
    description='This project is to create the directory tree to upload your project to Pypi',
    long_description=open('README.md').read(),  # Certifique-se de que o arquivo README.md esteja presente.
    long_description_content_type='text/markdown',
    url='https://github.com/batestin1/',
    project_urls={
        'Código fonte': 'https://github.com/batestin1/',
        'Download': 'https://github.com/batestin1/'
    },
    keywords='directory tree backup',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[  # Dependências necessárias para rodar seu pacote
        'pywin32',  # Adiciona a biblioteca win32api
    ],
    entry_points={
        'console_scripts': [
            'backup_tree=BackupTree.backupTree:main',  # Supondo que você tenha uma função main() no seu script
        ],
    },
)
