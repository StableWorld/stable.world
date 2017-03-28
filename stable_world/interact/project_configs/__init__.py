
from .base import ProjectConfigurator
from .circleci import CircleProjectHelper
from .default import CustomProjectHelper

ProjectConfigurator.register(CircleProjectHelper)
ProjectConfigurator.default(CustomProjectHelper)

__all__ = ('ProjectConfigurator', )
