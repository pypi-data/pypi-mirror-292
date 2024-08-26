from setuptools import setup, find_packages

setup(
    name='fsd_v2_universal',
    version='0.1.0',
    author='Zinley',
    author_email='dev@zinley.com',
    description='A brief description of your library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Zinley-dev/fsd_v2_universal',  # Replace with your library's URL
    packages=find_packages(),  # Automatically find package directories
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify the Python version required
    install_requires=[
        # List your library's dependencies here
        # 'somepackage>=1.0',
    ],
    extras_require={
        'dev': [
            'check-manifest',
        ],
    },
    include_package_data=True,  # Include files listed in MANIFEST.in
)
