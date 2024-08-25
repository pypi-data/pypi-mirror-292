from setuptools import setup, find_packages

setup(
    name='SizePred',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={'SizePred': ['models/*.joblib']},
    install_requires=[
        'numpy',
        'pandas',
        'scikit-learn',
        'joblib',
    ],
)