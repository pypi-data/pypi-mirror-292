from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='movoid_robotframework_requests',
    version='1.0.5',
    packages=find_packages(),
    url='',
    license='',
    author='movoid',
    author_email='bobrobotsun@163.com',
    description='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['requests',
                      'psutil',
                      'movoid_function>=1.7.1',
                      'movoid_package',
                      'movoid_robotframework',
                      'robotframework-requests',
                      ],
)
