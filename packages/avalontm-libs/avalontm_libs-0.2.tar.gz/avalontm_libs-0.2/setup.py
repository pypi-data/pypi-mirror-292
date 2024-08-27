from setuptools import setup

with open("./README.md", "r") as readme:
    long_description = readme.read()

setup(
    name='avalontm_libs',
    packages=['avalontm_libs'],
    version='0.2',
    description='Libreria simple para usarlo en python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='AvalonTM',
    author_email='',
    url='https://github.com/avalontm/avalonmt_libs',
    download_url='https://github.com/avalontm/avalonmt_libs/tarball/0.2',
    keywords=['mysql', 'database', 'data base'],
    classifiers=[],
    license='MIT',
    include_package_data=True,
    install_requires=[
         'mysql-connector-python>=9.0.0',
    ],
)