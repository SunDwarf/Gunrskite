# Config Example
# Copy this to config.py and edit as appropriate.

# SQLAlchemy database URI.
SQLALCHEMY_URI = "mysql+pymysql://gunrskite:gunrskite@localhost:3306/gunrskite"

# UDP listener bind data.
LISTENER_BIND = (
    "0.0.0.0",  # IP address to bind to.
    23887  # Port to bind to.
)


# Gunrskite settings.
INITIAL_POINTS = 1000

POINTS_ON_KILL = 3
POINTS_LOST_ON_DEATH = 2
