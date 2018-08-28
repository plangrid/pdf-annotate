#!groovy
node {
    env.NO_ELASTICSEARCH = 'true'
    env.NO_MONGO = 'true'
    env.NO_POSTGRES = 'true'
    env.NO_REDIS = 'true'
    env.NO_MOTO = 'true'
    env.NO_FAKES3 = 'true'

    branches = [
        "py2": [],
        "py3": [
            'DEFAULT_NOSETESTS=nosetests-3.4',
            'DEFAULT_PYTHON=python3',
            'DEFAULT_PIP=pip3'
        ]
    ]

    StandardBuild(
        parallelUnitTests: branches,
        publishLibrary: true,
        libraryName: "pdf-annotate",
    )
}
