from setuptools import setup, find_packages
import os

def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

setup(
    name='TheOGPlatformer',
    version='1.0',
    description='A simple yet fun platformer',
    author='Yusuf',
    author_email='yusufdeesawala72@gmail.com',
    packages=find_packages(),  # Automatically finds the packages
    install_requires=['pygame'],  # Read dependencies from requirements.txt
    include_package_data=True,
    package_data={
        'TheOGPlatformer': ['platformer/img/*.png','platformer/img/*.wav','platformer/levels/*'],  # Include other necessary files
    },
    entry_points={
        'console_scripts': [
            'start_game=platformer.main:run_game',  # Adjust to match your package structure
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)