from setuptools import find_packages, setup

VERSION = '0.1.321'
DESCRIPTION = 'Text Regularization for Unstructured Text from EMS Reports'
LONG_DESCRIPTION = 'Made by Michael Chary'

# Setting up
setup(
    name="hospitalpy",
    version=VERSION,
    author="Michael Chary",
    author_email="<mic9189@med.cornell.edu>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(where='src'),
    package_data={'hospitalpy': ['src/hospitalpy/assets/*']},
    package_dir={'': 'src'},
    include_package_data=True,
    keywords=['python', 'nlp', 'ems', 'global ems'],
    classifiers=[]
)
