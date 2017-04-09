
from .base import ProjectConfigurator
from .circleci import CircleProjectHelper
from .default import CustomProjectHelper

ProjectConfigurator.register('circleci', CircleProjectHelper)
ProjectConfigurator.register('custom', CustomProjectHelper)

ProjectConfigurator.default('custom')

__all__ = ('ProjectConfigurator', )
