from setuptools import setup, find_packages


setup(
    name='ditrans2cldf',
    version='1.0',
    description='',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    author='Johannes Englisch',
    author_email='johannes_englisch@eva.mpg.de',
    url='',
    keywords='data linguistics',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'cldfbench[glottolog]',
        'openpyxl',
        'pybtex',
        'unidecode'],
    entry_points={
        'cldfbench.scaffold': [
            'ditransitive_db=ditrans2cldf.scaffold:DitransDBTemplate'
        ],
    },
    extras_require={
        'dev': ['flake8'],
        'test': [
            'tox',
            'pytest',
            'pytest-cov',
            'coverage',
        ],
    },
    tests_require=[],
    test_suite="ditrans2cldf")
