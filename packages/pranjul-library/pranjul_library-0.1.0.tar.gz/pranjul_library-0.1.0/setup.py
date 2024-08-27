from setuptools import setup, find_packages

setup(
    name='pranjul_library',  # Replace with your package’s name
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
    author='Pranjul Shukla',
    author_email='spranjul2592@gmail.com',
    description='A library for returning string with alternate alphabates',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # License type
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',

)