from setuptools import setup

setup(
    entry_points={
        'sqlalchemy.dialects': [
            'gbasedbt = sqlalchemy_gbasedbt.dbtdb:GBasedbtDialect',
        ]
    },
    install_requires=['DbtPy~=3.0.5.6', 'SQLAlchemy<2'],
)
