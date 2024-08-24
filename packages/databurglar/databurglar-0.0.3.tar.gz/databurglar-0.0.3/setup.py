import setuptools


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

with open('plugin_requirements.txt') as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name='databurglar',
    version='0.0.3',
    python_requires='>=3.12.5',
    keywords='Data Collection, SqlAlchemy',
    description='SQLAlchemy Package for data tracking.',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    install_requires=install_requires,
    url='https://github.com/dpasse/databurglar',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points = {}
)
