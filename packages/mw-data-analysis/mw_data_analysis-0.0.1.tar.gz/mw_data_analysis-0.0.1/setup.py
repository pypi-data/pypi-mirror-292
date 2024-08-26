from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Package about analysis of mental disease and weather'
LONG_DESCRIPTION = 'A package including the analysis of relationship between mental disease and weather and an application based on a ML model'

# Setting up
setup(
       # the name must match the folder name 
        name="mental_weather", 
        version=VERSION,
        author="Shih-Yen Hung",
        author_email="<syhung@gapp.nthu.edu.tw>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        readme = "README.md",
        keywords=['python', 'first package'],
        classifiers= [
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ]
)