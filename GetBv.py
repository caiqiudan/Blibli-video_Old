import requests
from parsel import Selector
import json
import os


class GetBv():
    def __init__(self, bvid, page=1):
        '''
        bvid:视频号 eg:BV1hE411N7q2，str
        page: P几的视频，默认为1 int
        '''
        self.bvid = bvid
        self.page = page
        self.pg_dic, self.file_name, self.all_page = GetBv.get_name_pages(self)  # 视频名称表单、文件夹名称、总视频数
        # 表头
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
                        'Referer': 'https://www.bilibili.com',}
    
    # 获取视频网址
    def get_video_audio_urls(self):
        url = f'https://www.bilibili.com/video/{self.bvid}?p={self.page}'
        r = requests.get(url)
        selector = Selector(text=r.text)
        # 视频连接
        video_audio = selector.xpath('/html/head/script[5]/text()').getall()
        video_dic = video_dic = json.loads(video_audio[0][video_audio[0].index('{'):])['data']['dash']['video'] # 找到{}才能loads
        video_url = video_dic[0]['baseUrl']
        # 音频连接
        audio = video_dic = json.loads(video_audio[0][video_audio[0].index('{'):])['data']['dash']['audio']
        audio_url = audio[0]['baseUrl']
        return video_url, audio_url
    
    # 获取视频名称表单并创建存放视频的文件夹
    def get_name_pages(self):
        # 获取名称表单
        url = f'https://www.bilibili.com/video/{self.bvid}'
        r_ng = requests.get(url)
        selector = Selector(r_ng.text)
        
        video_message = selector.xpath('/html/head/script[6]/text()').getall()
        video_message = json.loads(video_message[0][video_message[0].index('{'):video_message[0].index('};')+1])      # 找到{}才能loads
        
        all_page = video_message['videoData']['videos']    # 总页数/视频数
        page_name_dic = {}             # 页数对应的名称
        for x in video_message['videoData']['pages']:
            page_name_dic[x['page']] = x['part']
            
        # 创建文件夹
        file_name = video_message['videoData']['title']
        if os.path.exists(file_name) == False: # 判断是否存在该文件夹
            os.mkdir(file_name)
            
        return page_name_dic, file_name,all_page
        
    # 获取video.m4s和audio.m4s格式的音频和视频
    def get_mp4(self):
        # bv_name: 视频名称
        bv_name = self.pg_dic[self.page]
        path = f'{self.file_name}/{bv_name}'    # 视频路径
        if os.path.exists(f'{bv_name}.mp4'):  # 判断是否存在该视频
            print(f'已存在第{self.page}P视频——{bv_name}.mp4')
        else:
            video_url, audio_url = GetBv.get_video_audio_urls(self)
            # 视频
            r_video = requests.get(video_url, headers=self.headers)

            with open(f'{path}_video.m4s', 'wb') as f:
                f.write(r_video.content)
            # 音频
            r_video = requests.get(audio_url, headers=self.headers)
            with open(f'{self.file_name}/{bv_name}_audio.m4s', 'wb') as f:
                f.write(r_video.content)
            # 合并视频
            order = f'ffmpeg -i "{path}_video.m4s" -i "{path}_audio.m4s" -codec copy "{path}.mp4"'  # 加引号是为了解决路径不能包含空格 . 的问题
            os.system(order)
            # 删除原来的音频+视频.m4s文件
            os.remove(f"{path}_audio.m4s")
            os.remove(f"{path}_video.m4s")

            print(f'成功爬取,第{self.page}P视频——{bv_name}')

if __name__ == '__main__':
    bvid = 'BV1Pt411G7my'           # ----视频的id----
    getBv = GetBv(bvid)
    max_page = getBv.all_page        # 获取最大页数
    page_list = list(range(1, max_page+1))   # ---爬取第几P视频的列表-，记得加1--
    print(f'###########开始爬取##########\n 本次爬取第{page_list}P的视频')
    
    for page in page_list:
        getBv.page = page
        getBv.get_mp4()
