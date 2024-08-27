from setuptools import setup, find_packages

setup(
    name='yh_olap',
    version='0.0.3',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'pyotp',
        'selenium',
        'webdriver_manager',
        'requests_toolbelt',
    ],
)