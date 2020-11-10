#pylint:skip-file

import setuptools
import versioneer

setuptools.setup(
    name="mcmock",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=setuptools.find_namespace_packages(include=['mcmock']),
    install_requires=[],
    python_requires=">=3.8"
)
