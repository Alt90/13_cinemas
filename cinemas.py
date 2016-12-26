import requests
import random
from bs4 import BeautifulSoup


TIMEOUT = 10


def fetch_afisha_page():
    return requests.get('http://www.afisha.ru/msk/schedule_cinema/')


def parse_afisha_list(raw_html):
    info = BeautifulSoup(raw_html.content, 'html.parser')
    movies_info = info.find_all("div", attrs={"class": "object"})
    proxy_list = get_proxies_list()
    movies_list = []
    for movie_info in movies_info:
        title = movie_info.find("h3", attrs={"class": "usetags"}).text
        count_cinemas = len(movie_info.find_all("td",
                                                attrs={"class": "b-td-item"}))
        rating, count_ratings = get_rating(title, proxy_list)
        movies_list.append({'title': title,
                            'count_cinemas': count_cinemas,
                            'rating': rating,
                            'count_ratings': count_ratings})
    return movies_list


def get_random_agent():
    agent_list = [
        'Mozilla/5.0 (X11; Linux i686; rv:50.0) Gecko/20100101 Firefox/50.0',
        'Opera/9.80 (Windows NT 6.2; WOW64) Presto/2.12.388 Version/12.17',
        'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:36.0) Gecko/20100101'
    ]
    return random.choice(agent_list)


def get_proxies_list():
    proxy_url = '%s://%s/api/proxy?anonymity=%s&token=%s' % (
        'http',
        'www.freeproxy-list.ru',
        'false',
        'demo')
    html = requests.get(proxy_url).text
    proxies = html.split('\n')
    return proxies


def get_random_proxy(proxy_list):
    return random.choice(proxy_list)


def get_html_movie(movie_title, proxy_list):
    headers = {'Accept': 'text/plain',
               'Accept-Encoding': 'UTF-8',
               'Accept-Language': 'Ru-ru',
               'Content-Type': 'text/html;charset=UTF-8',
               'User-Agent': 'Agent:%s' % get_random_agent(), }
    proxy_ip = get_random_proxy(proxy_list)
    proxy = {"http": proxy_ip}
    params = {'kp_query': movie_title,
              'first': 'yes'}
    print("proxy = %s, title = %s" % (proxy_ip, movie_title))
    html = requests.session().get('http://kinopoisk.ru/index.php',
                                  params=params,
                                  headers=headers,
                                  proxies=proxy,
                                  timeout=TIMEOUT)
    return html.content


def get_rating(movie_title, proxy_list):
    while True:
        try:
            info = BeautifulSoup(get_html_movie(movie_title, proxy_list),
                                 'html.parser')
            rating = info.find("span", class_="rating_ball").text
            rating_counts = info.find("span", class_="ratingCount").text
        except AttributeError:
            rating, rating_counts = '0', '0'
            break
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ProxyError,
                requests.exceptions.ReadTimeout) as error:
            print('Reconnect...')
        else:
            break
    return (rating, rating_counts)


def output_movies_to_console(movies, count=10):
    print('title - count cinemas - rating - count ratings')
    for movie in movies[:count]:
        print('%s - %s - %s - %s' % (movie['title'],
                                     movie['count_cinemas'],
                                     movie['rating'],
                                     movie['count_ratings']))


def sort_movies(movies_list):
    return sorted(movies_list,
                  key=lambda k: k['rating'],
                  reverse=True)


if __name__ == '__main__':
    afisha_page = fetch_afisha_page()
    movies_list = parse_afisha_list(afisha_page)
    movies_sorted_list = sort_movies(movies_list)
    output_movies_to_console(movies_sorted_list)
