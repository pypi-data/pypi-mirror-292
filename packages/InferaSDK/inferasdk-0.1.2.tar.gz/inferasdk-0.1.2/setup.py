from setuptools import setup

setup(
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        "local_scheme": "node-and-date",
    },
    setup_requires=['setuptools_scm'],
)