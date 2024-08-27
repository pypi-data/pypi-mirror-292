from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="iacob",
    version="1.0.1",

    description="Development of an interactive brain connectivity data mining tool",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Thibaud SCRIBE, Enzo CREUZET",
    author_email="thibaud.scribe@etu.univ-tours.fr, enzo.creuzet@etu.univ-tours.fr",
    url="https://scm.univ-tours.fr/projetspublics/lifat/iacob",
    
    python_requires='>=3.10, <3.13',
    install_requires=[
        'PyQt5>=5.15.0,<=5.15.10',
        'matplotlib>=3.5.0,<=3.9.1',
        'networkx>=3.0,<=3.3.0',
        'scipy>=1.8.0,<=1.14.0',
        'pyqtgraph>=0.11.0,<=0.13.7',
        
    ],

    packages=find_packages(),
    package_data={
        'iacob': ["resources/*", 
                  "resources/images/*"],
        '': ["requirements.txt"],
    },
    
    entry_points={
        'console_scripts': [
            'iacob-app=iacob.src.IACOB:run_app',
        ],
    },
)


