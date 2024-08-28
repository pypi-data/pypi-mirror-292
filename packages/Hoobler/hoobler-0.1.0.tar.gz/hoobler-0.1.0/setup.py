from setuptools import setup, find_packages

setup(
    name='Hoobler',
    version='0.1.0',
    packages=find_packages(include=['src', 'src.*']),
    py_modules=['main'],
    include_package_data=True,
    package_data={
        '': ['knowledge_base.json'],
    },
    install_requires=[
        'curses; platform_system!="Windows"',
        'windows-curses; platform_system=="Windows"'
    ],
    entry_points={
        'console_scripts': [
            'hoobler=main:main',
        ],
    },
    author='Pedro Ivo',
    author_email='pedro0513@gmail.com',
    description='Assistente I.A. com foco em ser uma central de atalhos.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vegedra/hoobler',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
