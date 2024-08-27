from setuptools import setup, find_packages

setup(
    name="allstarlink-keyed",
    version="0.1.4",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.0.0",
        "beautifulsoup4>=4.0.0",
        "rich>=13.0.0",
        "tenacity>=8.0.0"
    ],
    entry_points={
        'console_scripts': [
            'allstarlink-keyed=allstarlink_keyed.main:main',
        ],
    },
    author="Jon Poindexter W5ALC",
    description="A script to fetch and display currently keyed AllStarLink Nodes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/w5alc/allstarlink-keyed",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
