print(
    f"""
	__file__={__file__:<35}
	__name__={__name__:<20}
	__package__={__package__!s:<20}
	"""
)

from . import operators
from . import panels
from . import properties


def register():
    operators.register()
    panels.register()
    properties.register()


def unregister():
    operators.unregister()
    panels.unregister()
    properties.unregister()
