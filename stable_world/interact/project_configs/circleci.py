from os.path import isfile, join
from .base import ProjectConfigurator


class CircleProjectHelper(ProjectConfigurator):

    @classmethod
    def is_valid(cls, project_dir):
        if isfile(join(project_dir, 'circle.yml')):
            return True
        if isfile(join(project_dir, 'circle.yaml')):
            return True
