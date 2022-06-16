from bs4 import BeautifulSoup as bs
import requests
import csv
from multiprocessing import Pool

session = requests.Session()
def soupify(url):
    #print(url)
    page = session.get(url).content
    soup = bs(page, features='html.parser')
    return soup

grabbed = set()
followed = set()
def grab_links(page):
    soup = soupify(page)
    # these are links to recipes
    ends = soup.findAll(lambda tag: tag.name == 'a' and tag.get('class') == ['card-recipe-info', 'card-link'])
    for s in ends:
        grabbed.add(s['href'])

    # these are links to collections, which is just another page full of recipes
    leads = soup.findAll(lambda tag: tag.name == 'a' and tag.get('class') == ['card-link'])
    for l in leads:
        if l['href'] in followed:
            continue
        else:
            followed.add(l['href'])
        grab_links(base_url + l['href'])


base_url = "https://cooking.nytimes.com"
search_url = "https://cooking.nytimes.com/search?q=&page="

def scrape():
    for i in range(1, 500):
        if i >= 10 and i % 10 == 0:
            with open('recipe_urls.txt', mode='wt', encoding='utf-8') as handle:
                handle.write('\n'.join(list(sorted(grabbed))))
        print("processing page {}".format(i))
        old = len(grabbed)
        grab_links(search_url + str(i))
        print("page {} resulted in {} new recipes".format(i, len(grabbed) - old))

def recipe(page):
    soup = soupify(base_url + page)
    try:
        title = soup.find(lambda tag: tag.name == 'h1' and tag.get('class') == ['recipe-title', 'title', 'name']).text.strip()
        bylines = soup.select('div.nytc---recipebyline---bylinePart a')
        byline = ','.join([b.text for b in bylines])
    except: # if no author, we just say meh whatever
        print(base_url + page)
        return ''
    try:
        tags = soup.find(lambda tag: tag.name == 'div' and tag.get('class') == ['tags-nutrition-container']).text.strip()
    except:# if no tags, perhaps use the title as tags? ```tags = ', '.join([word.upper() for word in title.split(' ')])```
        tags = ''
    return ';'.join([page, title, byline, tags])

with open('recipe_urls.txt', 'r') as handle:
    recipes_urls = [l.strip() for l in handle]
with open('output2.txt', 'w') as out:
    with Pool(10) as p:
        l=p.map(recipe, recipes_urls)
    l = list(filter(None, l))
    out.write('\n'.join(l))

