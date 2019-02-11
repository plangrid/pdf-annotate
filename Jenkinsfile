#!groovy
node {
    env.NO_ELASTICSEARCH = 'true'
    env.NO_MONGO = 'true'
    env.NO_POSTGRES = 'true'
    env.NO_REDIS = 'true'
    env.NO_MOTO = 'true'
    env.NO_FAKES3 = 'true'

    env.PYTHON_TEST_COMMAND_OVERRIDE = 'tox'

    StandardBuild(
        publishLibrary: true,
        libraryName: "pdf-annotate",
    )
}
