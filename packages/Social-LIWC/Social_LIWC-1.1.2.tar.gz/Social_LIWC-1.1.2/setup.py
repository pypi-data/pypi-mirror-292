from setuptools import setup, find_packages

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='Social_LIWC',
    version='1.1.2',
    license='MIT License',
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=['fastapi', 'liwc', 'pandas'],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'Social_LIWC': ['dados/*.dic'],
    }
)