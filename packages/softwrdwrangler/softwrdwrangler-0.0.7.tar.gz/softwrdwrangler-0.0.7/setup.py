from setuptools import setup, find_packages
setup(
    name='softwrdwrangler',
    version='0.0.7',
    author='Md Robiuddin',
    author_email='mrrobi040@gmail.com',
    description='A package to wrangle software data in the cloud.',
    long_description=open('README.md').read(),  # Ensure you have a README.md file
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'boto3',
        'pandas'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.9',
    url='https://github.com/softwrdai/softwrdwrangler',
)
