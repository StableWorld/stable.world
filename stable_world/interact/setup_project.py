
from .project_configs import ProjectConfigurator


def setup_project(project_dir, client):

    project_config = ProjectConfigurator.detect(client, project_dir)

    project_config.setup_project_name()
    project_config.setup_project_env()
    project_config.setup_project_ci()
