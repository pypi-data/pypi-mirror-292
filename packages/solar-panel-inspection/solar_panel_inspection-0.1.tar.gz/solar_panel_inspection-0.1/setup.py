from setuptools import setup, find_packages

setup(
    name="solar-panel-inspection",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "roboflow", 
        "Pillow"
    ],
    entry_points={
        'console_scripts': [
            'solarpanel=solar_panel.core:solarpanel',
        ],
    },
    author="Mukesh Anand G",
    author_email="ai.mukeshanandg@gmail.com",
    description="A package to detect solar panels and save bounding box images.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/solar-panel-inspection",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
