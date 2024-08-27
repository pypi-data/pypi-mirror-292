from setuptools import setup, find_packages

setup(
    name='tableau-vizportal-client',
    version='1.0.7',
    description='A helper addon for TableauServerClient to simplify making API calls to the Tableau Vizportal API',
    author='Rody Zakovich',
    author_email='rodyzakovich@gmail.com',
    url='https://github.com/FsuLauncherComp/tableau-vizportal-client',
    packages=find_packages(),
    install_requires=[
        'tableauserverclient>=0.11'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)