from setuptools import setup, find_packages

setup(
    name="DjangoEssentials",
    version="0.1.8",
    author="Coder Mungan",
    author_email="codermungan@gmail.com",
    description="Reusable Django models, utils and storages",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CoderMungan/DjangoEssentials",
    packages=find_packages(),
    include_package_data=True,
    package_data={"djangoessentials": ["migrations/*.py"]},
    install_requires=[
        "Django>=3.2",
        "django-storages[boto3]>=1.11",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
