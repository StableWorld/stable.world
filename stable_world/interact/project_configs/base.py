from random import choice
import abc
from . import words


def random_project_name():
    return '%s-%s' % (choice(words.adjectives), choice(words.nouns))


class ProjectConfigurator(abc.ABC):
    """
    """
    CONFIGS_HELPERS = []
    CONFIGS_HELPER_DEFAULT = None

    @staticmethod
    def register(detector):
        ProjectConfigurator.CONFIGS_HELPERS.append(detector)

    @staticmethod
    def default(detector):
        ProjectConfigurator.CONFIGS_HELPER_DEFAULT = detector

    @classmethod
    def detect(cls, client, project_dir):
        for detector in ProjectConfigurator.CONFIGS_HELPERS:
            if detector.is_valid(project_dir):
                return detector(client, project_dir)

        if cls.CONFIGS_HELPER_DEFAULT:
            return cls.CONFIGS_HELPER_DEFAULT(client, project_dir)

    def __init__(self, client, project_dir):
        self.client = client
        self.client = client
        self.project_dir = project_dir

    @abc.abstractmethod
    def setup_project_name(self):
        pass

    @abc.abstractmethod
    def setup_project_env(self):
        pass

    @abc.abstractmethod
    def setup_project_ci(self):
        pass
