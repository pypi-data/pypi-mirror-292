# My library for shortening links

A simple library for shortening links

## Installation

**You can install this library using pip**:
```
pip install Cut4Url
```
## How to Short
```
from Cut4Url import Cut4Url

shortener = Cut4Url.Short()

shortened_url = shortener.clck("https://google.com")
print("Clck:", shortened_url)

shortened_url = shortener.ulvis("https://google.com")
print("Ulvis:", shortened_url)

shortened_url = shortener.isgd("https://google.com")
print("Is.gd:", shortened_url)

shortened_url = shortener.cleanuri("https://google.com")
print("CleanURI:", shortened_url)

shortened_url = shortener.abre("https://google.com")
print("Abre:", shortened_url)

shortened_url = shortener.shorturl("https://google.com")
print("ShortUrl:", shortened_url)

shortened_url = shortener.de("https://google.com")
print("De:", shortened_url)

```
## How To Check Short Url
```
from Cut4Url import Cut4Url

shortener = Cut4Url.Short()
shortened_url = shortener.check("https://in.mt/6ER")
print("Short Url: "+shortened_url[0])
print("Long Url: "+shortened_url[1])