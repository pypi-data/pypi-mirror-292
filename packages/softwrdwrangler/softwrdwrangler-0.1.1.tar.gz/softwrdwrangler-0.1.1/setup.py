from setuptools import setup, find_packages
setup(
    name='softwrdwrangler',
    version='0.1.1',
    author='Md Robiuddin',
    author_email='mrrobi040@gmail.com',
    description='A package that provides utilities for data wrangling with AWS S3, pandas, and geojson.',
    long_description=open('README.md').read(),  # Ensure you have a README.md file
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'boto3',
        'pandas',
        'geojson',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.9',
    url='https://github.com/softwrdai/softwrdwrangler',
    keywords=['aws', 's3', 'pandas', 'geojson', 'pickle', 'data wrangling'],
)
