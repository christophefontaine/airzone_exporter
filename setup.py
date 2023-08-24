from setuptools import setup, find_packages


setup(
    name='airzone_exporter',
    desc='AirZone Prometheus Exporter',
    version='1.0.0',
    author="Christophe Fontaine",
    url="https://github.com/christophefontaine/airzone_exporter",
    packages=find_packages(include=['airzone_exporter']),
    package_data={'airzone_exporter': ['airzone-exporter.service']},
    include_package_data=True,
    install_requires=[
        'prometheus_client',
        'requests',
        'systemd'
    ],
    entry_points={
        'console_scripts': ['az-exporter=airzone_exporter.airzone_exporter:main']
    }
)
