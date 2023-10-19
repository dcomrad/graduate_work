from .film_work_scheme import film_work_scheme
from .genre_scheme import genre_scheme
from .person_scheme import person_scheme

schemas = {'film_work': film_work_scheme, 'genre': genre_scheme, 'person': person_scheme}

__all__ = ('schemas',)
