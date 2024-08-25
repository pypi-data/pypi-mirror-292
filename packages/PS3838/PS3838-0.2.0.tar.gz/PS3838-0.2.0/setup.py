from setuptools import find_packages, setup

# Set the description of the package and the long description
with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

DESCRIPTION = "A package to interact with the PS3838 API, especially to retrieve odds and bet automatically."

# Call the setup function
setup(
    name='PS3838',
    version='0.2.0',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown', 
    author='Gaëtan Le Fournis',
    author_email='gaetanlf22@gmail.com',
    url='https://github.com/gaetanlefournis/PS3838.git',
    license='MIT',
    keywords='PS3838, bet, betting, odds, football, soccer',
    packages=find_packages(),
    classifiers=[
        # Development Status
        'Development Status :: 4 - Beta', # Still in development

        # License
        'License :: OSI Approved :: MIT License',

        # Programming Language
        'Programming Language :: Python', 
        'Programming Language :: Python :: 3',  
        'Programming Language :: Python :: 3.7',  
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        
        # Natural Language
        'Natural Language :: English', 
    ],
    install_requires=[
        'anyio>=4.4.0',
        'httpx>=0.27.0',
        'Levenshtein>=0.25.1',
        'python-dotenv>=1.0.1',
        'PyYAML>=6.0.1',
        'requests>=2.32.3',
        'rapidfuzz>=3.9.4',
    ],
    extras_require={
        'dev': [
            'pytest>=8.2.2',
            'pytest-cov>=5.0.0',
        ],
    },

    # A URL to a website containing documentation for your package.
    project_urls={
        'Bug Reports': 'https://github.com/gaetanlefournis/PS3838/issues',
        'Source': 'https://github.com/gaetanlefournis/PS3838',
    },
)
