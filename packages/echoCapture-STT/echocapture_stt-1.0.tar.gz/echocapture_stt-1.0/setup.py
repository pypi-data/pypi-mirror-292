from setuptools import setup,find_packages

setup(
    name= 'echoCapture_STT',
    version= '1.0',
    author= 'Jagu Nayak',
    description='This is speech to text package for youtube and other website created by Jagu Nayak'
)
packages = find_packages(),

install_requirements = [
    'selenium',
    'webdriver_manager',
    'os',
    'time'
]