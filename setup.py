#pylint:skip-file

import setuptools
import versioneer

setuptools.setup(
    name="mcmock",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=setuptools.find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            "mcmock = mcmock.__main__:main"
        ],
    },
    python_requires=">=3.8"
)
