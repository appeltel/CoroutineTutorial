import requests

BASE_URL = 'https://ericappelt.com/animals/'


def speak(animal, session):

    response = session.get('{}/{}'.format(BASE_URL, animal))
    response.raise_for_status()
    sound = response.text

    return 'The {} says "{}".'.format(animal, sound)


def main():
    animals = ['cow', 'pig', 'chicken']
    session = requests.Session()
    for animal in animals:
        response = speak(animal, session)
        print(response)


if __name__ == '__main__':
    main()
