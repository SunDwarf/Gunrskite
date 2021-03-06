# Config Example
# Copy this to config.py and edit as appropriate.

# SQLAlchemy database URI.
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://gunrskite:gunrskite@localhost:3306/gunrskite"

# UDP listener bind data.
LISTENER_BIND = (
    "0.0.0.0",  # IP address to bind to.
    23887  # Port to bind to.
)

# Some long and utterly unguessable secret key here.
SECRET_KEY = 'yourkeyhere'

# Gunrskite settings.
INITIAL_POINTS = 1000

POINTS_ON_KILL = 3
POINTS_LOST_ON_DEATH = 2

# Steam API key.
STEAM_API_KEY = ""