from flask import Flask, request, send_file, render_template
import requests, shutil
from bs4 import BeautifulSoup as bs

from modules import has_path, read_json, write_json


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
temp_root = 'responses'

def get_meaning(lang: str = 'english-chinese-simplified', text: str = '', try_again: bool = True):
  fp = f'{temp_root}/{text}.json'
  if has_path(fp): return read_json(fp)
  reqt = sess.get(f"https://dictionary.cambridge.org/dictionary/{lang}/{text}")
  soup = bs(reqt.text, 'html.parser')
  try:
    title = soup.find('span', {'class': 'hw dhw'}).string
    meaning = [i.string for i in soup.find_all('span', {'class': 'trans dtrans dtrans-se break-cj'})]
    if reqt.status_code == 404 or not title: raise 'Page Not Found'
    data = {
      'title': title or '',
      'meaning': meaning,
      'preview': '\n'.join([f'{i + 1}. {meaning[i]}' for i in range(len(meaning))]),
      'status_code': 200
    }
  except Exception as e:
    if try_again > 0:
      soup = bs(sess.get(f'https://dictionary.cambridge.org/spellcheck/english-chinese-simplified/?q={text}').text, 'html.parser')
      text = soup.find('li', {'class': 'lbt lp-5 lpl-20'}).find('a').string
      if text: return get_meaning(lang, text, False)
    data = {
      'title': '404 Page Not Found',
      'meaning': [],
      'preview': 'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.',
      'status_code': 404
    }
  write_json(fp, data)
  return data


@app.route('/')
def route_index():
  return render_template('index.html', query=request.args.get('q') or '')

@app.route('/api', methods=['GET', 'POST'])
def route_api():
  res = get_meaning(request.args.get('lang'), request.args.get('text'))
  if request.method == 'GET':
    return render_template('result.html', data=res), res['status_code']
  else:
    return res['preview'], res['status_code']

@app.route('/favicon.ico')
def route_favicon():
  return send_file(f'static/favicon.ico')

import gunicorn
from admin import admin

app.register_blueprint(admin, url_prefix='')

shutil.rmtree('__pycache__', ignore_errors=True)
shutil.rmtree(temp_root, ignore_errors=True)

if __name__ == '__main__':
  app.run(debug=True, threaded=True, port=3000)