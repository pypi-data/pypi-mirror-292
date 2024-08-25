from setuptools import setup, find_packages

setup(
    name='unique_multiples_library',  # Replace with your package’s name
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
    author='Juhi Rastogi',  
    author_email='juhirastogi048@gmail.com',
    description='A library for checking multiples of 2 and 5.',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # License type
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',

)