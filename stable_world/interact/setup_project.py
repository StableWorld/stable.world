
from .project_configs import ProjectConfigurator


def setup_project(app, project_dir, ty=None):

    if ty:
        project_config = ProjectConfigurator.get(ty, app.client, project_dir)
    else:
        project_config = ProjectConfigurator.detect(app.client, project_dir)

    project_config.setup()

    project_config.setup_project_name()
    project_config.setup_project_env()
    project_config.setup_project_ci()

    project_config.success()
