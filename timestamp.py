from datetime import datetime
import re
import time
import sublime
import sublime_plugin

def getParseResult(text):
    #patten1 匹配10位整数时间戳（1493283600）
    pattern1 = re.compile('^\d{10}')
    match1 = pattern1.match(text)

    #pattern2 匹配可读时间格式（2017-04-27 17:00:00）
    pattern2 = re.compile('^(\d{4})-(\d{1,2})-(\d{1,2})\s(\d{1,2}):(\d{1,2}):(\d{1,2})')
    match2 = pattern2.match(text)

    if text in ('now'):
        result = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elif text in ('ts', 'timestamp'):
        result = str(time.time()).split('.')[0]
    elif match1:
        timestamp = int(match1.group(0))
        timeArray = time.localtime(timestamp)
        result = time.strftime('%Y-%m-%d %H:%M:%S', timeArray)
    elif match2:
        timeArray = time.strptime(text, "%Y-%m-%d %H:%M:%S")
        result = str(time.mktime(timeArray)).split('.')[0]
    return result

class TimestampCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for s in self.view.sel():
            if s.empty() or s.size() <= 1:
                break

            # 只处理第一个Region
            text = self.view.substr(s)
            print(text)

            # 得到转换结果
            result = getParseResult(text)

            # 进行文本替换并弹窗显示
            self.view.replace(edit, s, result)
            self.view.show_popup(result, sublime.HIDE_ON_MOUSE_MOVE_AWAY, -1, 600, 600)
            break