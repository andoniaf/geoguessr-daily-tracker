from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geoguessr-daily-tracker",
    version="0.1.0",
    author="Andoni Alonso",
    author_email="geoguessr-daily-trac.handbag544@passmail.net",
    description="Track your GeoGuessr daily challenge scores",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/geoguessr-daily-tracker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=1.9.2",
        "requests>=2.27.0",
        "google-auth>=2.22.0",
        "google-api-python-client>=2.52.0",
    ],
    entry_points={
        "console_scripts": [
            "geoguessr-daily-tracker=geoguessr_daily_tracker.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "geoguessr_daily_tracker": ["data/*.csv"],
    },
)
