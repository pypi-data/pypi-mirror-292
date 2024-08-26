import setuptools

setuptools.setup(
    name="hamonsoft-ai-database",
    version="0.0.18",
    description="Hamonsoft Company Database Python Version Package",
    author="Hamonsoft AI",
    python_requires=">=3.8, <4",
    packages=setuptools.find_packages(),
    install_requires=[
        'mysql-connector-python==9.0.0',
        'impyla==0.19.0'
    ],
    license="MIT",
)
