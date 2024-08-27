from setuptools import setup, find_packages

setup(
    name='WrdSmth',
    version='0.1.0',
    description='A Python library for text preprocessing.',
    author='Nazaryan Artem Karapetovich',
    author_email='spanishiwasc2@gmail.com',
    packages=find_packages(),
    install_requires=[
        'nltk',
        'scikit-learn',
    ],
    classifiers=[  # Optional: Classifiers help categorize your package
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # Replace with your chosen license
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)