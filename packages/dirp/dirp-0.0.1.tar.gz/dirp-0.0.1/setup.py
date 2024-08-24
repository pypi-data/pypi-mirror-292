from setuptools import setup, find_packages

setup(
    name="dirp",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'dirp=dir_print:main',  # 'mytool' is the command, 'my_script' is the module, and 'main' is the function
        ],
    },
    author="Tripp Dow",
    author_email="trippdow@gmail.com",
    description="Command-line recursive pretty printer for directories.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/prettytrippy/dirp",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
