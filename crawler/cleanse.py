import re
from bs4 import BeautifulSoup

def decomposeClasses(element, classList, soup):

    for classname in classList:
        for e in soup.find_all(element, {"class": classname}):
            e.decompose()

def decomposeID(element, ID, soup):

    for e in soup.find_all(element, {"id": ID}):
        e.decompose()

with open("table.json") as f:
    
    x = f.readlines()
    for i in x:
        i = i[1:-2]
        i = i.replace("\\n","")
        i = i.encode().decode("unicode-escape")
        #regex substitution
        try:
            results = re.findall(r'href="[A-Za-z0-9&?=$#%.-_:/;]*"', i)
            for r in results:
                newr =  'href="https://en.wikipedia.org/' + r[7:-1] + '"'
                i = i.replace(r, newr)
            
            soup = BeautifulSoup(i, features="html.parser")
            
            divClasses = ['stub','mw-references-wrap', 'mw-references-wrap', 'mw-editsection', 'navbox']
            spanClasses = ['mw-editsection']
            supClasses = ['reference']
        
            decomposeClasses("div", divClasses, soup)
            decomposeClasses("span", spanClasses, soup)
            decomposeClasses("sup", supClasses, soup)
            decomposeID("span", "References", soup)
            
            print(soup)

        except:
            continue
