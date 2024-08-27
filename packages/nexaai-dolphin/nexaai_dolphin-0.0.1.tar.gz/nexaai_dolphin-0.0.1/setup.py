from setuptools import setup, find_packages

setup(
    name="nexaai-dolphin",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "transformers",
        "torch"
    ],
    include_package_data=True,
    description="A package for the Dolphin model under the Nexa AI framework",
    long_description="The Dolphin model is part of the Nexa AI framework, designed for advanced natural language processing tasks.",
    long_description_content_type="text/plain",
    author="Alex Chen, Zack Li",
    author_email="octopus@nexa4ai.com",
    url="https://github.com/NexaAI/nexa-dolphin",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    keywords="nexa ai dolphin model machine-learning",
)