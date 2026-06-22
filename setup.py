from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tetra-os',
    version='1.0.0',
    author='Walter Calmels K.',
    author_email='walter.calmels@example.com',
    description='Self-improving multi-level optimization and scientific discovery system',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/waltercalmelsk/tetra-os',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Intended Audience :: Science/Research',
    ],
    python_requires='>=3.8',
    install_requires=[
        'numpy>=1.19.0',
        'matplotlib>=3.3.0',
        'pandas>=1.2.0',
        'flask>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'tetra=tetra_os.__main__:main',
        ],
    },
)
