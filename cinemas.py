import requests
import random
from bs4 import BeautifulSoup
import logging


TIMEOUT = 10
HANDLER = logging.FileHandler('cinemas.log')
HANDLER.setLevel(logging.DEBUG)
LOGGER = logging.getLogger('spam_application')
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(HANDLER)


def fetch_afisha_page():
    return requests.get('http://www.afisha.ru/msk/schedule_cinema/')


def parse_afisha_list_page(raw_html):
    info = BeautifulSoup(raw_html.content, 'html.parser')
    movies_info = info.find_all("div", attrs={"class": "object"})
    for movie_info in movies_info:
        title = movie_info.find("h3", attrs={"class": "usetags"}).text
        count_cinemas = len(movie_info.find_all("td",
                                                attrs={"class": "b-td-item"}))
        yield {'title': title,
               'count_cinemas': count_cinemas}


def get_random_agent():
    """При реконекте меняет браузер подключения"""
    agent_list = [
        'Mozilla/5.0 (X11; Linux i686; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Opera/9.80 (Windows NT 6.2; WOW64) Presto/2.12.388 Version/12.17',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101'
    ]
    return random.choice(agent_list)


def get_proxies_list():
    proxy_url = 'http://www.freeproxy-list.ru/api/proxy'
    params = {'anonymity': 'false',
              'token': 'demo'}
    html = requests.get(proxy_url, params=params).text
    proxies = html.split('\n')
    return proxies


def get_html_by_title(movie_title, proxy_list):
    try:
        params = {'kp_query': movie_title,
                  'first': 'yes'}
        headers = {'Accept': 'text/plain',
                   'Accept-Encoding': 'UTF-8',
                   'Accept-Language': 'Ru-ru',
                   'Content-Type': 'text/html;charset=UTF-8',
                   'User-Agent': 'Agent:%s' % get_random_agent(), }
        proxy = {"http": random.choice(proxy_list)}
        html = requests.session().get('http://kinopoisk.ru/index.php',
                                      params=params,
                                      headers=headers,
                                      proxies=proxy,
                                      timeout=TIMEOUT)
    except (requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ProxyError,
            requests.exceptions.ReadTimeout) as error:
        return None
    else:
        return html.content


def get_html_by_title_multiconnection(movie_title, proxy_list):
    while True:
        html = get_html_by_title(movie_title, proxy_list)
        if html is not None:
            return html
        else:
            LOGGER.info('Reconnect...')


def get_rating_by_title(movie_title, proxy_list):
    try:
        movie_html = get_html_by_title_multiconnection(movie_title, proxy_list)
        info = BeautifulSoup(movie_html, 'html.parser')
        rating = info.find("span", class_="rating_ball").text
        rating_counts = info.find("span", class_="ratingCount").text
    except AttributeError:
        return '0', '0'
    else:
        return (rating, rating_counts)


def get_ratings_to_movies_list(movies_list):
    proxy_list = get_proxies_list()
    for movie in movies_list:
        LOGGER.info('parse = %s' % movie['title'])
        rating, count_ratings = get_rating_by_title(movie['title'], proxy_list)
        yield {'title': movie['title'],
               'count_cinemas': movie['count_cinemas'],
               'rating': rating,
               'count_ratings': count_ratings}


def output_movies_to_console(movies, count=10):
    print('title - count cinemas - rating - count ratings')
    for movie in movies[:count]:
        print('%s - %s - %s - %s' % (movie['title'],
                                     movie['count_cinemas'],
                                     movie['rating'],
                                     movie['count_ratings']))


def sort_movies_by_ratings(movies_list_with_ratings):
    return sorted(movies_list_with_ratings,
                  key=lambda movie: movie['rating'],
                  reverse=True)


if __name__ == '__main__':
    afisha_page = fetch_afisha_page()
    movies_list = parse_afisha_list_page(afisha_page)
    movies_list_with_ratings = get_ratings_to_movies_list(movies_list)
    sorted_movies_list = sort_movies_by_ratings(movies_list_with_ratings)
    output_movies_to_console(sorted_movies_list)
