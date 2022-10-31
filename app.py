from flask import Flask, request, send_file, redirect, render_template, Blueprint
import os, random, requests, json
from bs4 import BeautifulSoup as bs


app = Flask(__name__)
app.config['SECRET_KEY'] = 'cambridge-dict-api-137'
appName = 'Cambridge Dictionary API'
my_token = 'SNH7rRi1nplE9P3qZnW4yLgrlCiHlOcZiDPqh8wrnxGF59QNN0momslRr3mZsQZs'
sess = requests.session()
sess.headers = {
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
  'accept-language': 'en-US,en;q=0.9',
  'referer': 'https://dictionary.cambridge.org/',
  'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin'
}

@app.route('/')
def route_index():
  return render_template('index.html')

@app.route('/api', methods=['GET', 'POST'])
def route_api():
  lang = request.args.get('lang') or 'english-chinese-simplified'
  text = request.args.get('text') or ''
  soup = bs(sess.get(f"https://dictionary.cambridge.org/dictionary/{lang}/{text}").text, 'html.parser')
  try: text = soup.find('span', {'class': 'hw dhw'}).string
  except: pass
  soup = [i.string for i in soup.find_all('span', {'class': 'trans dtrans dtrans-se break-cj'})]
  if request.method == 'GET':
    return render_template('result.html', text=text, result=json.dumps(soup, separators=(',',':'), ensure_ascii=False))
  else:
    return '\n'.join([f'{i+1}. {soup[i]}' for i in range(len(soup))])

@app.route('/random-bg')
def route_random_bg():
  _dir = 'static/background'
  return send_file(f'{_dir}/{random.choice(os.listdir(_dir))}')

@app.route('/favicon.ico')
def route_favicon():
  return send_file(f'static/favicon.ico')

import gunicorn, shutil
from admin import admin

app.register_blueprint(admin, url_prefix='')

shutil.rmtree('__pycache__', ignore_errors=True)

if __name__ == '__main__':
  app.run(debug=True, threaded=True, port=3000)