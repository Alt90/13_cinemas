import requests
from bs4 import BeautifulSoup


def fetch_afisha_page():
    return requests.get('http://www.afisha.ru/msk/schedule_cinema/')


def parse_afisha_list(raw_html):
    info = BeautifulSoup(raw_html.content, 'html.parser')
    movies_info = info.find_all("div", attrs={"class": "object"})
    movies_list = []
    for movie_info in movies_info:
        title = movie_info.find("h3", attrs={"class": "usetags"}).text
        count_cinemas = len(movie_info.find_all("td",
                                                attrs={"class": "b-td-item"}))
        movies_list.append({'title': title,
                            'count_cinemas': count_cinemas})
    return movies_list


def fetch_movie_info(movie_title):
    pass


def output_movies_to_console(movies, count=10):
    print('title - count cinemas')
    for movie in movies[:count]:
        print('%s - %s' % (movie['title'], movie['count_cinemas']))


if __name__ == '__main__':
    afisha_page = fetch_afisha_page()
    movies_list = parse_afisha_list(afisha_page)
    output_movies_to_console(movies_list, len(movies_list))
