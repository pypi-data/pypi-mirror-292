from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='ADRINA_STT',
        version='0.1',
        description="Package",
        long_description=readme(),
        author='Anirban',
        author_email='a9irba9das@gail.com',
        url='https://github.com/adam-dz/package',
        packages=find_packages(exclude=[])
)
packages = find_packages(),
install_requirements = ['selenium', 'webdriver_manager']