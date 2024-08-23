from setuptools import setup, find_packages

setup(
    name='json_exception_logger',  # Updated name
    version='2.0.0',
    author='Aayush Chaudhary',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
    ],
    python_requires='>=3.6',
)
