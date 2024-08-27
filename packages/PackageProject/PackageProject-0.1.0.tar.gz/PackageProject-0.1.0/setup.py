from setuptools import setup,find_packages
setup(
    name="PackageProject",
    version="0.1.0",
    description="A simple example package",
    author="Oussama Bouchhioua",
    author_email="Oussama.Bouchhioua@ifm.com",
    url="https://gitlab-ee.dev.ifm/deboucou/myproject",
    packages=find_packages(),  # Automatically find all packages
    install_requires=[
        # Add any dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)