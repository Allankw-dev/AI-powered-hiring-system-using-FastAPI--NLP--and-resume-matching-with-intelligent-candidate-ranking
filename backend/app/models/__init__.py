"""Import every model so Base.metadata knows about all tables."""
from .user import User  # noqa: F401
from .job import Job  # noqa: F401
from .resume import Resume  # noqa: F401
from .application import Application  # noqa: F401
from .email_log import EmailLog  # noqa: F401
