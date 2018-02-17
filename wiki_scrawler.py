import requests
import re
import random
from pprint import pprint
from bs4 import BeautifulSoup as bs

INF = 1000000007

def name(link):
    xml = requests.get(link).text
    soup = bs(''.join(xml), "xml")
    m = soup.find('h1')
    return m.string

def createLink(ending):
    return "https://en.wikipedia.org"+ending

def validInt(l, r, inp=''):
    if inp == '':
        inp = input()
    while inp == '' or re.search(r'\D', inp) or int(inp) < l or int(inp) > r:
        print('I need valid ints, you fool!')
        inp = input()
    return int(inp)

class Crawler:
    def __init__(self):
        self.history = []
        self.current = ''
        self.steps = 0
        self.destination = ''
        self.route = []

    def start(self):
        inp = ';'
        while 1:
            print("Give me an english wikipedia link with a 'See also' heading")
            inp = input()
            try:
                requests.get(inp)
            except ValueError:
                continue
            break
        print('Choose a difficulty (any number greater than 0)')
        dif = validInt(1, INF)
        print('Processing...')
        self.destination = self.randomArticle(inp, dif)
        print("Get to '" + name(self.destination) + "' article in the least number of moves")
        self.crawl(inp)

    def noLinks(self):
        print("Sorry, no 'See also' links in this page")
        self.history.pop()
        if len(self.history):
            self.crawl(self.history[-1])
        else:
            self.start()

    def findLinks(self):
        xml = requests.get(self.current).text
        soup = bs(''.join(xml), "xml")
        m = soup.find('div', attrs={"class" : "mw-parser-output"})
        cur = m.next_element
        links = []
        while cur and cur.next_sibling:
            if cur.name == 'h2' and cur.find('span') and cur.find('span')['id'] == 'See_also':
                while 1:
                    if re.search(r'navigation|presentation', str(cur)):
                        cur = cur.next_sibling
                    if cur.name == 'ul':
                        for u in cur.find_all('a', href=re.compile('[^.]*'), title=re.compile('.*')):
                            links.append(createLink(u['href']))
                        return links
                    cur = cur.next_element
                return links
            cur = cur.next_sibling
        return links

    def interact(self, links):
        if len(links) == 0:
            self.noLinks()
        else:
            for i in range(len(links)):
                print(str(i+1) + ' : ' + name(links[i]))
            print('Type in a number or "0" to go back...')
            inp = input()
            if inp == 'p':
                print('Hint:')
                for p in self.route:
                    print(p)
            inp = validInt(0, len(links), inp)
            if inp != 0:
                self.crawl(links[inp-1])
            else:
                self.history.pop()
                if len(self.history):
                    self.crawl(self.history[-1])
                else:
                    print("No way higher...")
                    self.crawl(createLink(self.current))

    def crawl(self, link):
        self.current = link
        self.steps += 1
        self.history.append(self.current)
        print('-'*50)
        print('Current: ' + name(self.current))
        print('-'*50)
        if link == self.destination:
            print("Congratulations, you've made it!\nYour result is " + str(self.steps-1) + " moves.")
            return None
        links = self.findLinks()
        self.interact(links)

    def randomArticle(self, start, difficulty):
        Bob = Crawler()
        Bob.current = start
        res = Bob.goDeep(difficulty)
        self.route = Bob.route
        return res

    def goDeep(self, depth):
        self.route.append(name(self.current))
        if depth:
            links = self.findLinks()
            if links == []:
                return self.current
            follow = random.choice(self.findLinks())
            self.current = follow
            return self.goDeep(depth-1)
        else:
            return self.current

if __name__ == '__main__':
    Jack = Crawler()
    Jack.start()
