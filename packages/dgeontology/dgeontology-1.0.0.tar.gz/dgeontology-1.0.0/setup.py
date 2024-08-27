import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name = 'dgeontology',
    version = '1.0.0',
    author = 'Michal Bukowski',
    author_email = 'michal.bukowski@tuta.io',
    description = 'Library for gene set enrichment analysis (ontology analysis) and visualisation',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/michalbukowski/dge-ontology',
    project_urls = {
        'Bug Tracker': 'https://github.com/michalbukowski/dge-ontology/issues',
    },
    classifiers = [
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
    ],
    packages = ['dgeontology'],
    python_requires = '>=3.6',
    install_requires=[
        'pandas>=2.2',
        'matplotlib>=3.8',
        'scipy>=1.12'
    ]
)

