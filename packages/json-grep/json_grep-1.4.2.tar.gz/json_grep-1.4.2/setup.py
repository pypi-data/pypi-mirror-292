import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from jsongrep.libs.setuptools import get_file_content, get_file_content_as_list

pwd = os.path.dirname(__file__)

packages = find_packages()
VERSION = get_file_content(os.path.join(pwd, "jsongrep/VERSION"))
DOCUMENTATION_MD = get_file_content(os.path.join(pwd, "README.md"))
requirements = get_file_content_as_list(os.path.join(pwd, "requirements.txt"))


def _postinstall():
    subprocess.call(["activate-global-python-argcomplete", "--user", "--yes"])
    subprocess.call(["eval", "$(register-python-argcomplete jgrep)"])
    subprocess.call(["eval", "$(register-python-argcomplete jsongrep)"])
    subprocess.call(["eval", "$(register-python-argcomplete json-grep)"])

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        _postinstall()


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        _postinstall()


print(f"packages: {packages}")
print(f"requirements: {requirements}")

setup(
    name="json-grep",
    version=VERSION,
    license='MIT',
    author='Ales Adamek',
    author_email='alda78@seznam.cz',
    description='Filtering JSON dict keys from STDOUT',
    long_description=DOCUMENTATION_MD,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/alda78/json-grep",
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    include_package_data=True,  # MANIFEST.in
    zip_safe=False,  # aby se spravne vycitala statika pridana pomoci MANIFEST.in
    cmdclass={
        'install': PostInstallCommand,
    },
    entry_points={
        'console_scripts': [
            'jsongrep=jsongrep.main:main',
            'json-grep=jsongrep.main:main',
            'jgrep=jsongrep.main:main',
        ],
    },
)
