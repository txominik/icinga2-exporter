#from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import setup, find_packages

from manage_version import get_version

def read(fname):
    return open(join(dirname(__file__), fname)).read()

setup(
    name='icinga2-exporter',
    version=get_version(),
    packages=['icinga2_exporter'],
    author='thenodon',
    author_email='anders@opsdis.com',
    url='https://github.com/opsdis/icinga2-exporter',
    license='GPLv3',
    include_package_data=True,
    zip_safe=False,
    description='A Prometheus exporter for Icinga2 (nexmart modifications)',
    python_requires='>=3.6',
    install_command='--install-layout=deb'
)

