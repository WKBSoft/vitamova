# coding=utf-8
import ssl
import urllib
import re

def translate(word):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen('https://translate.googleapis.com/translate_a/single?client=gtx&sl=uk&tl=en&dt=t&q='+word,context=ctx)
    html = str(response.read())
    translation_start = html.find("[\"") + 2
    translation_stop = html.find("\"",translation_start)
    return html[translation_start:translation_stop]

def clear_blanks(my_list):
    for i in list(reversed(range(len(my_list)))):
        if my_list[i][0] == '':
            del my_list[i]
    return my_list

def reformat_header(file_data):
    data_start = file_data.find("<section>")
    file_data = file_data[data_start:len(file_data)]
    data_end = file_data.find("<binary")
    if data_end >= 0:
        file_data = file_data[0:data_end]
    file_data = file_data.replace("<title>","<h1>")
    file_data = file_data.replace("</title>","</h1>")
    file_data = file_data.replace("–","--")
    return file_data

def label_tags(file_data):
    tag_start = file_data.find("<")
    tag_end = 0
    content_list = []
    while tag_start >=0:
        content_list.append([file_data[tag_end:tag_start],"notag"])
        tag_end = file_data.find(">",tag_start)+1
        content_list.append([file_data[tag_start:tag_end],"tag"])
        tag_start = file_data.find("<",tag_end)
    content_list.append([file_data[tag_end:len(file_data)],"notag"])
    content_list = clear_blanks(content_list)
    return(content_list)

def label_spaces(content_list):
    for i in reversed(range(len(content_list))):
        if content_list[i][1] == "notag":
            content_list[i][0] = content_list[i][0].replace('\xc2\xa0',' ')
            words = re.split('[,.\s!?\-]+',content_list[i][0])
            sub_list = []
            end = 0
            data = content_list[i][0]
            for x in words:
                start = data.find(x,end)
                sub_list.append([content_list[i][0][end:start],"space"])
                end = start + len(x)
                sub_list.append([content_list[i][0][start:end],"word"])
            sub_list.append([content_list[i][0][end:len(content_list[i][0])],"space"])
            content_list = content_list[0:i]+sub_list+content_list[i+1:len(content_list)]
    content_list = clear_blanks(content_list)
    return(content_list)

def a_tags(content_list):
    for i in range(len(content_list)):
        if content_list[i][1] == "word":
            content_list[i][0] = "<a class='text-body' onclick=\"tran_uk('"+content_list[i][0]+"')\">"+content_list[i][0]+"</a>"
    return content_list

def page_divide(content_list,wordcount):
    word_i = 0
    pages = []
    page = ""
    for x in content_list:
        page += x[0]
        if x[1] == "word":
            word_i += 1
        if word_i > wordcount:
            if x[0] == "</p>":
                pages.append(page)
                page = ""
                word_i = 0
    pages.append(page)
    return(pages)

def return_pages(content,wordcount,page):
    label_list = label_spaces(label_tags(reformat_header(content)))
    linked_list = a_tags(label_list)
    page_list = page_divide(linked_list,wordcount)
    page = int(page)
    if page == 0:
        page_list = page_list[0:2]
    elif page == len(page_list) - 1:
        page_list = page_list[len(page_list)-2:len(page_list)]
    else:
        page_list = page_list[page-1:page+2]
    page_str = "~~".join(page_list)
    return page_str




