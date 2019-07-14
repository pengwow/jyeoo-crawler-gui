
aa = [{'id':'1','p_id':'2'},
      {'id':'2','p_id':''},
      {'id':'3','p_id':''},
      {'id':'4','p_id':'1'},
      {'id':'5','p_id':'2'}
      ]
dd = {'id': '30b677a8-a638-11e9-a827-38378beebca7', 'parent_id': '30b62084-a638-11e9-9967-38378beebca7', 'library_id': '11a1b125-bdb4-4a8d-973f-3f5cc5367ed7', 'pk': '11a1b125-bdb4-4a8d-973f-3f5cc5367ed7~10aa6869-7bf3-49ff-9589-5e30bc9f54b6~G8', 'name': 'G8：反比例函数与一次函数的交点问题', 'child': []}

for k in dd.values():
    print(len(k))