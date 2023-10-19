from .film import Film, FilmShortView
from .genre import Genre
from .person import Person

models_by_str = {
    'Film': Film,
    'FilmShortView': FilmShortView,
    'Genre': Genre,
    'Person': Person
}
