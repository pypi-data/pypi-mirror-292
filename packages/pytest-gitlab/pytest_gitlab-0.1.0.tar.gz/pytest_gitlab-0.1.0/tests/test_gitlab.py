def test_hello_gitlab(gl):
    project = gl.projects.create(name='my-project')
    assert project.name == 'my-project'


def test_create_project(project):
    assert project.name


def test_docker_project_name(docker_compose_project_name):
    assert docker_compose_project_name == 'pytest-python-gitlab'
