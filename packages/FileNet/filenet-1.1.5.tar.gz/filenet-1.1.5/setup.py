from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup( 
	name='FileNet', 
	version='1.1.5', 
    packages=find_packages(),
	description='A Python package for creating 2D, 3D vizulization of directory and files with their hierarchical relations.', 
	author='Aditya Narayan', 
	author_email='adityaan277@gmail.com', 
    long_description=long_description,
    long_description_content_type="text/markdown",
	install_requires=[  
		'networkx', 
        'matplotlib',
        'plotly',
        'scipy'
	], 
    entry_points={
        "console_scripts":[
            "FileNet = FileNet:hello",
        ],
    },
) 
