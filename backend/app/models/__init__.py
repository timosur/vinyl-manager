# Import all models here so alembic can discover them
from app.models.artist import Artist
from app.models.label import Label
from app.models.release import Release
from app.models.track import Track
from app.models.artist_release_association import ArtistReleaseAssociation
from app.models.label_release_association import LabelReleaseAssociation

