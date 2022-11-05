from flask import Blueprint, request, render_template
admin = Blueprint('admin', __name__)
import os, time
from app import my_token, del_temp


@admin.before_request
def admin_before_request():
  adm_key = request.cookies.get('cd-api-admin')
  if adm_key != my_token:
    if request.method == 'GET': return render_template('login.html')
    else: return 'You are not logined.'

@admin.route('/admin137/')
def route_admin():
  return render_template('admin.html')

@admin.route('/push', methods=['POST'])
def route_push():
  print('pushing project to GitHub...')
  del_temp()
  os.system('pipreqs --encoding=utf8 --force .')
  os.system('git add .')
  os.system(f'git commit -am "update on {time.strftime("%Y/%m/%d, %H:%M:%S")}"')
  os.system('git push')
  return 'success'