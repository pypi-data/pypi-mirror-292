from setuptools import setup, find_packages

setup(
    name="yesilfilm",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    description="Yeşilçam filmleri seçme ve oynatma uygulaması.",
    author="Dogukan",
    author_email="nagamiisbruh@gmail.com",
    url="https://github.com/Handsomeskull/yesilfilm.git",  # GitHub repo URL'nizi buraya ekleyin
    entry_points={
        'console_scripts': [
            'yesilfilm = yesilfilm.main:film_secimi',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
