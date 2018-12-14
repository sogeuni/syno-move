# -*- coding: utf-8 -*-
from synopy.base import Connection
from synopy.api import DownloadStationTask
import re
import subprocess
from subprocess import CalledProcessError

DOWN_ROOT=u'/volume2/download/'
TV_SUFFIX=r'(\ \d{1,2}-\d{1,2}회\ 합본)?\.E\d{1,3}(\.END)?\.\d{6}\.(720|1080)p-NEXT(.mp4)?'
TV_ROOT=r'tv/'
REMOTE_NAME=u'remote'

def move_file(task):

  # print(task)
  
  id = task.get('id')
  type = task.get('type')
  status = task.get('status')
  title = task.get('title')
  src_dir = task.get('additional').get('detail').get('destination')

  # print(id)
  # print(type)
  # print(status)
  # print(title)

  p = re.compile(TV_SUFFIX)

  # 다운이 완료되었다면 옮기자
  if type == 'bt' and status == 'seeding':
    # 옮길 경로 만들기
    try:
      m = p.search(title)

      if m:
        dest_dir=TV_ROOT + p.sub('', title) + "/" + title
        cmd = 'rclone move "' + src_dir + '/' + title + '" "' + REMOTE_NAME + ':' + dest_dir + '"'
        print(cmd)
        result = subprocess.check_output(cmd, shell=True)
        print("cmd: " + result)
      else:
        # TODO: movie
        return False
    except (TypeError, AttributeError) as e:
      print(e)
      return False
    except CalledProcessError:
      print('CalledProcessError')
      return False

    return True
  
conn = Connection('https', 'sogn.io', port=5001)
conn.authenticate('', '')

dstask_api = DownloadStationTask(conn, version=1)
# Use the 'list' query method to see the running tasks
resp = dstask_api.list(additional='detail,file')

if resp.is_success():
  tasks = resp.payload.get('data').get('tasks')

  for task in tasks:
    result = move_file(task)

    if result:
      print('move_file = ' + result)
      result = dstask_api.delete(task.get('id'))
      print(result)
      # TODO: noti
    else:
      print('move error')