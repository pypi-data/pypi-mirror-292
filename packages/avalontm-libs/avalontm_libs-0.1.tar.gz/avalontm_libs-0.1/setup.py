from setuptools import setup

readme = open("./README.md", "r")


setup(
    name='avalontm_libs',
    packages=['avalontm_libs'],  # this must be the same as the name above
    version='0.1',
    description='Libreria simple para usarlo en python',
    long_description=readme.read(),
    long_description_content_type='text/markdown',
    author='AvalonTM',
    author_email='',
    # use the URL to the github repo
    url='https://github.com/avalontm/avalonmt_libs',
    download_url='https://github.com/avalontm/avalonmt_libs/tarball/0.1',
    keywords=['mysql', 'database', 'data base'],
    classifiers=[ ],
    license='MIT',
    include_package_data=True
)