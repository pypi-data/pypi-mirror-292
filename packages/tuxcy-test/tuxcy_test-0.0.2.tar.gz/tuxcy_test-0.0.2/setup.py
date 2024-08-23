from setuptools import setup, find_packages

setup(
    name="tuxcy-test",
    version="0.0.2",
    packages=find_packages(),
    install_requires=[
      "requests",
      "click"
    ],
    entry_points={
        'console_scripts': [
            'geo-auto-install = geo_auto_install.autoinstall:main',
        ]
    }
)
