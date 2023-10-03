from datetime import date
import factory
from filmapi.models import User, Film, Actor


class UserFactory(factory.Factory):
    username: str = factory.Sequence(lambda n: "user%d" % n)
    email: str = factory.Sequence(lambda n: "user%d@mail.com" % n)
    password: str = "mypwd"

    class Meta:
        model = User


class FilmFactory(factory.Factory):
    title: str = factory.Sequence(lambda n: f"Test Film {n}")
    title_original: str = "Original Title"
    poster: str = "poster_url"
    rating: float = 7.5
    description: str = "Film description"
    release_date: date = date(2023, 9, 26)
    budget: str = "Budget"
    distributed_by: str = "Distributor"
    length: int = 120
    trailer: str = "trailer_url"

    class Meta:
        model = Film


class ActorFactory(factory.Factory):
    name: str = factory.Sequence(lambda n: f"Test Actor {n}")
    birthday: date = date(2023, 9, 26)
    is_active: bool = True

    class Meta:
        model = Actor
