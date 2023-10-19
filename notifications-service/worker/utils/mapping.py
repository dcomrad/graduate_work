from data.movies import JsonDataFetcher as MovieDataFetcher
from data.templates import JsonDataFetcher as TemplateDataFetcher
from data.users import JsonDataFetcher as UserDataFetcher


def send_template_service_request(template_id):
    data_fetcher = TemplateDataFetcher()
    return data_fetcher.fetch_template_data(str(template_id))

def send_movie_service_request(movie_id):
    data_fetcher = MovieDataFetcher()
    return data_fetcher.fetch_movie_data(str(movie_id))

def send_user_service_request(user_id):
    data_fetcher = UserDataFetcher()
    return data_fetcher.fetch_user_data(str(user_id))

services_dict = {"movie_id":send_movie_service_request, "user_id":send_user_service_request,
                 "template_id":send_template_service_request}

def make_service_request(service_name, id):
    return services_dict[service_name](id)
