import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='omf_sample_library_preview',
    version='0.1.1_preview',
    author='AVEVA',
    license='Apache 2.0',
    author_email='samples@osisoft.com',
    description='A preview of an OMF client library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/osisoft/sample-omf_library_preview-python',
    packages=setuptools.find_packages(),
    install_requires=['requests>=2.28.2', 'python-dateutil>=2.8.2'],
    tests_require=[
        'pytest>=7.0.1',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)
