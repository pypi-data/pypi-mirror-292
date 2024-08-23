from setuptools import setup, find_packages

setup( 
	name='FileNet', 
	version='1.0.1', 
    packages=find_packages(),
	description='A Python package for creating 2D, 3D vizulization of directory and files with their hierarchical relations.', 
	author='Aditya Narayan', 
	author_email='adityaan277@gmail.com', 
	install_requires=[  
		'networkx', 
        'matplotlib',
        'plotly'
	], 
    entry_points={
        "console_scripts":[
            "FileNet = FileNet:hello",
        ],
    },
) 
