from setuptools import setup, find_packages

setup(
    name='syncify_music',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # List your dependencies here
    ],
    entry_points={
        'console_scripts': [
            'syncify_music=main:syncify',
        ],
    },
    author='collin',
    author_email='collinbarlage@gmail.com',
    description='Syncs spotify playlists with local json',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/collinbarlage/syncify',
    license='CC0-1.0 license',
)