import json, os

def has_path(fp: str) -> bool:
  return os.path.exists(fp)

def read_file(fp: str) -> str:
  return open(fp, mode='r', encoding='utf-8').read()

def read_json(fp: str) -> object:
  return json.loads(read_file(fp))

def write_file(fp: str, s: str):
  # 将物件写入档案
  fp = fp.replace('\\', '/')
  dir_fp = fp.split('/')
  if len(dir_fp) > 1:
    dir_fp = '/'.join(dir_fp[:-1])
    # 检查并生成路径（若无）
    if not has_path(dir_fp): os.makedirs(dir_fp)
  open(fp, mode='w+', encoding='utf-8').write(s)

def write_json(fp: str, data: dict):
  # 将物件写入 json 格式档案
  write_file(fp, json.dumps(data, ensure_ascii=False, separators=(',',':')))