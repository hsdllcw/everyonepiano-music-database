# python3.7
import os
import sys
import shutil
import urllib3
from bs4 import BeautifulSoup
import html2text as ht
import json

# 创建连接
http = urllib3.PoolManager()
text_maker = ht.HTML2Text()
init_music_no = "0000000"


def delete_exists_file(down_load_dir):
    # 移除.exists文件可重复执行脚本
    for root, dirs, files in os.walk(down_load_dir):
        for name in files:
            if name == ".exists":
                file_path = os.path.join(root, name)
                os.remove(file_path)


def download(i, music_no, file_path):
    # noinspection PyBroadException
    try:
        res = http.request(
            "GET",
            "https://www.everyonepiano.cn/Music/down/"
            + i + "/" + music_no
        )
        with open(file_path, "wb") as file:
            file.write(res.data)
            print(file_path)
    except Exception:
        download(i, music_no, file_path)


def saveMusicInfo(dir_path, music_no, soup: BeautifulSoup):
    breadcrumbs = soup.find_all(name="ol", attrs={"class": "breadcrumb"})[0].find_all(name="li")
    author_element = soup.find_all(name="div", attrs={"class": "EOPReadInfoTxt"})[0].find_all("li")[0]
    # 处理html格式文件中的内容
    context = soup.find_all(name="div", attrs={"id": "MusicInfoTxt2"})[0]
    for hidden_xs in context.find_all(name="div", attrs={"class": "hidden-xs"}):
        hidden_xs.extract()
    text = text_maker.handle(str(context))
    # 写入处理后的内容
    read_me_file_path = dir_path+'/README.md'
    if not os.path.exists(read_me_file_path):
        with open(read_me_file_path, 'w') as f:
            f.write(text)
    music_info = {
        "title": breadcrumbs[-1].text,
        "author": author_element.find_all("a")[0].text,
        "musicType": breadcrumbs[-2].text,
        "musicNo": music_no
    }
    info_file_path = dir_path+'/info.json'
    if not os.path.exists(info_file_path):
        with open(info_file_path, 'w') as f:
            json.dump(music_info, f, ensure_ascii=False)
    return music_info


def main(down_load_dir=(os.path.expanduser('./'))):
    print("下载目录:" + down_load_dir)
    delete_exists_file(down_load_dir)
    # 发送请求，获取总钢琴曲数
    res = http.request('GET', "https://www.everyonepiano.cn/Music")
    soup = BeautifulSoup(res.data, features="html.parser")
    # 获取总音乐数
    count = int(soup.find_all(name="div", attrs={"class": "EOPPageNo"})[0].find_all(name="span")[0].text)
    last_error_page_count = 0
    # i = 12405
    i = 0
    # 不会吧不会吧不会真有人不知道count怎么用吧
    while i < count or last_error_page_count < 10:
        music_no = init_music_no[0:len(init_music_no) - len(str(i))] + str(i)
        print("正在获取资源" + music_no + "的信息...")
        res = http.request("GET", "https://www.everyonepiano.cn/Music-" + str(i) + "-")
        soup = BeautifulSoup(res.data, features="html.parser")
        breadcrumbs = soup.find_all(name="ol", attrs={"class": "breadcrumb"})
        if len(breadcrumbs) > 0:
            last_error_page_count = 0
            author_element = soup.find_all(name="div", attrs={"class": "EOPReadInfoTxt"})[
                0].find_all("li")[0]
            if "歌手/作者" in author_element.text:
                author = author_element.find_all("a")[0].text + " - "
            else:
                author = ""
            author = author.replace("/", " ")
            breadcrumbs = breadcrumbs[0].find_all("li")
            dir_path = down_load_dir + breadcrumbs[-2].text
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            title = breadcrumbs[-1].text.replace("/", " ")
            music_dir = dir_path + "/" + title
            file_name = author + title + ".eop"
            file_path = music_dir + "/" + file_name
            if not os.path.exists(music_dir):
                os.makedirs(music_dir)
            repeat_music_dir = music_dir + "/" + str(i)
            if (
                    (
                        os.path.exists(file_path)
                        and not os.path.exists(repeat_music_dir)
                        and os.path.exists(music_dir + "/.exists")
                    )
                    or not os.path.exists(file_path)
            ):
                if os.path.exists(file_path) and not os.path.exists(repeat_music_dir):
                    os.makedirs(repeat_music_dir)
                    music_dir = repeat_music_dir
                    file_path = music_dir + "/" + file_name
                print("正在下载:")
                # 下载
                print(saveMusicInfo(music_dir, music_no, soup))
                download(str(i), music_no, file_path)
            else:
                if os.path.exists(repeat_music_dir):
                    music_dir = repeat_music_dir
                    file_path = music_dir + "/" + file_name
                if not os.path.exists(music_dir + "/.exists"):
                    with open(music_dir + "/.exists", "wb") as file:
                        file.close()
                saveMusicInfo(music_dir, music_no, soup)
                print(file_name + "\t已经下载")
        else:
            print("资源" + str(i) + "不存在")
            count += 1
            last_error_page_count += 1
        i += 1
    delete_exists_file(down_load_dir)


#####################################################################################################################
# 根据曲谱列表来获音乐取信息
# for div_MITitle in filter(lambda div: div.get("class") is not None and "MITitle" in div.get("class"),
# soup.find_all("div")): musicList.append({ "title": list(filter(lambda a: a.get("class") is not None and "Title" in
# a.get("class"), div_MITitle.find_all("a")))[ 0].get("title"), "MImusic_no": list(filter( lambda div_MImusic_no:
# div_MImusic_no.get("class") is not None and "MImusic_no" in div_MImusic_no.get("class"), div_MITitle.find_all(
# "div")))[ 0].text })
#####################################################################################################################


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except IndexError:
        main()
