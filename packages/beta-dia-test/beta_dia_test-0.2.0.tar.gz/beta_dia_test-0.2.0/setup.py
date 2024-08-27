from setuptools import setup, find_packages

setup(
    name='beta_dia_test',
    version='0.2.0',
    packages=find_packages(),
    description='A cool project that does something awesome',
    author='Song Jian',
    license='MIT',
    install_requires=[
        'cupy>=12.2.0',
        'h5py>= 3.9.0',
        'matplotlib>=3.6.2',
        'networkx>=3.1',
        'numba>=0.58.1',
        'numpy>=1.23.5',
        'pandas>=2.2.2',
        'python_lzf>=0.2.4',
        'pyzstd>=0.15.9',
        'scikit_learn>=1.3.0',
        'scipy>=1.14.1',
        'statsmodels>=0.14.0',
        'torch>=2.1.1',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'beta_dia_test=beta_dia_test.main:main',
        ],
    },
)

