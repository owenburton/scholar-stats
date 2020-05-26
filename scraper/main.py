from flask import Flask
from selenium import webdriver
import chromedriver_binary

app = Flask(__name__)

options = webdriver.ChromeOptions()
options.headless = True
