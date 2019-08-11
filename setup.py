from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read()

setup(
    name='HoM-PoC',
    version='0.0.1',
    packages=['houseofmisfits', 'houseofmisfits.test'],
    install_requires=requirements,
    license='Proprietary',
    test_suite='houseofmisfits.test',
    classifiers=[
        'License :: Other/Proprietary License'
    ]
)
