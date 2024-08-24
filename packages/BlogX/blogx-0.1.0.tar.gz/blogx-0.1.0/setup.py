from setuptools import setup, find_packages

setup(
    name='BlogX',
    version='0.1.0',
    author='laysath',
    author_email='faithleysath@gmail.com',
    description='a simple and pure blog generator based on html + css + python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/faithleysath/BlogX',
    packages=find_packages(),
    install_requires=[
        'typer',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'blogx = BlogX.CLI:app',
        ],
    },
)
