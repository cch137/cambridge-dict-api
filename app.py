from flask import Flask, request, send_file, render_template, redirect
import requests, shutil, time, threading
from bs4 import BeautifulSoup as bs

from modules import has_path, get_ctime, read_json, write_json, json_dumps


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

def del_temp():
  shutil.rmtree('__pycache__', ignore_errors=True)
  shutil.rmtree(temp_root, ignore_errors=True)

def get_meaning(lang: str = 'english-chinese-simplified', text: str = ''):
  text = text.strip()
  fp = f'{temp_root}/{text}.json'
  if has_path(fp):
    if time.time() - get_ctime(fp) < 3600: # 缓存在一个小时过后无效
      return read_json(fp)
  reqt = sess.get(f"https://dictionary.cambridge.org/dictionary/{lang}/{text}")
  soup = bs(reqt.text, 'html.parser')
  try:
    title = soup.find('span', {'class': 'hw dhw'}).text
    meaning = [
      {
        'word': i.find('span', {'class': 'hw dhw'}).text,
        'pos': i.find('span', {'class': 'pos dpos'}).text,
        'gram': i.find('span', {'class': 'gram dgram'}),
        'guide': i.find('span', {'class': 'guideword dsense_gw'}),
        'defs': [
          {
            'en': j.find('div', {'class': 'def ddef_d db'}).text,
            'tr': j.find('span', {'class': 'trans dtrans dtrans-se break-cj'}).text,
            'eg': [
              {
                'en': k.find('span', {'class': 'eg deg'}).text,
                'tr': k.find('span', {'class': 'trans dtrans dtrans-se hdb break-cj'}).text
              } for k in j.find_all('div', {'class': 'examp dexamp'})
            ]
          } for j in i.find_all('div', {'class': 'def-block ddef_block'})
        ]
      } for i in soup.find_all('div', {'class': 'pr entry-body__el'})
    ]
    for i in range(len(meaning)):
      if meaning[i]['gram']: meaning[i]['gram'] = meaning[i]['gram'].text.replace('or', '/').replace(' ', '')
      else: meaning[i]['gram'] = ''
      if meaning[i]['guide']: meaning[i]['guide'] = meaning[i]['guide'].text
      else: meaning[i]['guide'] = ''
      for j in range(len(meaning[i]['defs'])):
        if meaning[i]['defs'][j]['tr'][-1] not in ['；', '。']:
          if j + 1 == len(meaning[i]['defs']): 
            meaning[i]['defs'][j]['tr'] += '。'
          else:
            meaning[i]['defs'][j]['tr'] += '；'
    if reqt.status_code == 404 or not title: raise 'Page Not Found'
    data = {
      'title': title or '',
      'lang': lang,
      'word': text,
      'meaning': meaning,
      'preview': ' '.join([' '.join([f"{j + 1}. {i['defs'][j]['en']} {i['defs'][j]['tr']}" for j in range(len(i['defs']))]) for i in meaning]),
      'trans': '\n'.join(['\n'.join([j['tr'] for j in i['defs']]) for i in meaning]),
      'status_code': 200
    }
  except Exception as e:
    soup = bs(sess.get(f'https://dictionary.cambridge.org/spellcheck/{lang}/?q={text}').text, 'html.parser')
    title = soup.find('h1', {'class': 'lpb-10 lbb'}).text
    if title == 'Your search terms did not match any entries.':
      meaning = []
      preview = 'We cannot find any entries matching kvblkbana. Please check you have typed the word correctly.'
    else:
      title = title.split(' ')
      title = f"{' '.join(title[:3])} \"{' '.join(title[3:])}\""
      meaning = [i.find('a').text.strip() for i in soup.find_all('li', {'class': 'lbt lp-5 lpl-20'})]
      preview = 'We have these words with similar spellings or pronunciations:'
    data = {
      'title': title,
      'lang': lang,
      'word': text,
      'meaning': meaning,
      'preview': preview,
      'trans': '',
      'status_code': 404
    }
  try: write_json(fp, data)
  except Exception as e: print(e)
  return data

@app.route('/')
def route_index():
  return render_template('index.html', query=request.args.get('q') or '')

@app.route('/api', methods=['GET', 'POST'])
def route_api():
  lang = request.args.get('lang') or request.args.get('l') or 'english-chinese-simplified'
  word = (request.args.get('word') or request.args.get('w')).replace('/', '').replace('\\', '')
  _type = request.args.get('type') or request.args.get('t') or 'preview'
  res = get_meaning(lang, word)
  if _type != 'json': res = res[_type]
  if _type == 'meaning' or _type == 'json': res = json_dumps(res)
  return res

@app.route('/dict/<lang>/<word>')
def route_dict(lang, word):
  res = get_meaning(lang or 'english-chinese-simplified', word.replace('/', '').replace('\\', ''))
  if request.args.get('raw'): return res['preview']
  elif request.method == 'POST': return res['preview']
  else: return render_template('result.html', data=res)

@app.route('/favicon.ico')
def route_favicon():
  return send_file(f'static/favicon.ico')

@app.route('/wakeup', methods=['POST'])
def route_wakeup():
  return 'success'


import gunicorn
from admin import admin

app.register_blueprint(admin, url_prefix='')

del_temp()

if __name__ == '__main__':
  app.run(debug=True, threaded=True, port=3000)