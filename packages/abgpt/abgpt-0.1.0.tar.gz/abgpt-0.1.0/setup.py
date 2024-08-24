from setuptools import setup, find_packages

setup(
    name="abgpt",
    version="0.1.0",
    author="Desmond Kuan, Amir Barati Farimani",
    author_email="barati@cmu.edu",
    description="AbGPT: De Novo B-Cell Receptor Design via Generative Language Modeling",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/deskk/AbGPT",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "tqdm",
    ],
    entry_points={
        'console_scripts': [
            'abgpt_generate=abgpt.main_module:main',  # Entry point for your CLI tool
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Specify the Python versions supported
)