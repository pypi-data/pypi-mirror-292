from setuptools import setup, find_packages

setup(
    name="data-visualization-package",
    version="0.1.5",
    author="Gustavo",
    author_email="gustavovicencotti@gmail.com",
    description="Data visualization package with graphics and interactivity support",
    long_description="Detailed description of the data visualization package",
    long_description_content_type="text/markdown",
    url="https://github.com/gvicencotti/data_visualization_package",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'plotly'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.8',
)