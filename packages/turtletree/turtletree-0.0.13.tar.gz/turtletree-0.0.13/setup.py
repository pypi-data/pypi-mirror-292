from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='turtletree',
    version='0.0.13',
    description='Data transform library written by Jaehak Lee',
    author='Jaehak Lee',
    author_email='leejaehak87@gmail.com',
    url='https://github.com/jaehakl/turtletree',
    install_requires=['numpy', 'pandas', 'matplotlib',],
    packages=find_packages(exclude=[]),
    keywords=['data', 'database', 'array', 'matrix'],
    python_requires='>=3.6',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: Apache Software License'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
)