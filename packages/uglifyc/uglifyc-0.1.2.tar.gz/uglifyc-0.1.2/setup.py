from setuptools import setup, find_packages


from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='uglifyc',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'uglifyc=uglifyc.main:uglify',
        ],
    },
    author='Muxutruk',
    author_email='156070698+Muxutruk2@users.noreply.github.com',
    description='Uglify C code',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Muxutruk2/uglify',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)
