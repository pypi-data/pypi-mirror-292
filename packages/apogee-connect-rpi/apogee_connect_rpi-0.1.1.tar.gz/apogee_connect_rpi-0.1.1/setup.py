# For help with building, packaging, and uploading to PyPI, visit:
# https://packaging.python.org/en/latest/tutorials/packaging-projects/
# and
# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
#
# TLDR; For just building and uploading, `python -m build` and then `twine upload dist/*` (Get API token from Bitwarden vault)
#

from setuptools import setup
from setuptools.command.install import install
import os
import shutil

def get_version(rel_path):
    with open(rel_path) as f:
        exec(f.read())
    return locals()['__version__']

class PostInstallCommand(install):
    def run(self):
        install.run(self)

        readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
        home_dir = os.path.expanduser("~")
        apogee_dir = os.path.join(home_dir, "Apogee", "apogee_connect_rpi")
        os.makedirs(apogee_dir, exist_ok=True)
        shutil.copy(readme_file, apogee_dir)

        print("Thank you for installing Apogee Connect for Raspberry Pi.")
        print("For official documentation, please visit: https://pypi.org/project/apogee-connect-rpi")
        print(f"The README file can also be found at: {apogee_dir}/README.md")

setup(
    version=get_version("apogee_connect_rpi/version.py"),
    cmdclass= {
        'install': PostInstallCommand,
    },
)