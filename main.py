# python3.7
import os
import sys
import shutil
import urllib3
from bs4 import BeautifulSoup

# 创建连接
http = urllib3.PoolManager()


# 移除.exists文件可重复执行脚本
def delete_exists_file(down_load_dir):
    for root, dirs, files in os.walk(down_load_dir):
        for name in files:
            if name == ".exists":
                file_path = os.path.join(root, name)
                os.remove(file_path)
                yield file_path


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
    except Exception:
        download(i, music_no, file_path)


def main(down_load_dir=(os.path.expanduser('./'))):
    print("下载目录:" + down_load_dir)
    delete_exists_file(down_load_dir)
    # 发送请求，获取总钢琴曲数
    init_music_no = "0000000"
    res = http.request('GET', "https://www.everyonepiano.cn/Music")
    soup = BeautifulSoup(res.data, features="html.parser")
    # 获取总音乐数
    count = int(soup.find_all(name="div", attrs={"class": "EOPPageNo"})[0].find_all(name="span")[0].text)
    last_error_page_count = 0
    i = 12286
    # 不会吧不会吧不会真有人不知道count怎么用吧
    while i < count or last_error_page_count < 10:
        music_no = str(i)
        print("正在获取资源" + music_no + "的信息...")
        res = http.request("GET", "https://www.everyonepiano.cn/Music-" + music_no + "-")
        soup = BeautifulSoup(res.data, features="html.parser")
        breadcrumbs = soup.find_all(name="ol", attrs={"class": "breadcrumb"})
        if len(breadcrumbs) > 0:
            last_error_page_count = 0
            author_element = soup.find_all(name="div", attrs={"class": "EOPReadInfoTxt"})[0].find_all("li")[0]
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
            source = dir_path + "/" + title + ".eop"
            if not os.path.exists(music_dir):
                os.makedirs(music_dir)
            if not os.path.exists(source):
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
                        file_path = repeat_music_dir + "/" + " - " + file_name
                    print("正在下载:")
                    # 下载
                    print({
                        "title": breadcrumbs[-1].text,
                        "author": author_element.find_all("a")[0].text,
                        "musicType": breadcrumbs[-2].text,
                        "musicNo": init_music_no[0:len(init_music_no) - len(music_no)] + str(i)
                    })
                    download(str(i), init_music_no[0:len(init_music_no) - len(music_no)] + str(i), file_path)
                else:
                    if os.path.exists(repeat_music_dir):
                        file_path = repeat_music_dir + "/" + file_name
                    if not os.path.exists(music_dir + "/.exists"):
                        with open(music_dir + "/.existsh", "wb") as file:
                            file.close()
                    print(file_name + "\t已经下载")
            else:
                shutil.move(source, file_path)
            print(file_path)
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
