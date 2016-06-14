from selenium import webdriver

browser = webdriver.PhantomJS()
browser.get('http://localhost:8000')

assert 'Django' in browser.title
