小黄油翻译器

# 配置方式：
**已知会被360弹窗拦截强力模式拦截，加入白名单或者直接关了**  

**v2.1版本更新设置图形界面，点击蓝色方块打开**  

**文件目录不能有中文**  

修改config.ini文件进行配置。区域选择默认F2，翻译默认F1。**进入区域选择后按Esc键退出，按空格键确认**。  

```
[BaiduOCR]
appid = 
appkey = 
secretkey = 

[BaiduTranslate]
appid = 
appkey = 
from_lang = jp
to_lang = zh


[Other]
font = 华康方圆体W7 18
font_color = #DC143C
; 是否使用本地OCR
is_localOCR = 1
; 文字显示延迟
show_text_dely = 0.7
; 区域选择键
select_area_key = F2
; 除此设置之外回车键也是翻译键
translate_key = Z
```
注册百度服务后在管理控制台创建应用可以得到密钥，复制到配置文件的对应位置即可：  
百度OCR：https://cloud.baidu.com/product/ocr_general  
百度翻译：https://api.fanyi.baidu.com  （**注册后创建通用翻译服务**）  

两者均可领取免费额度，其中百度翻译服务额度较多。  

百度OCR免费额度较少，**配置文件中is_localOCR设为1可开启本地OCR**（0关闭），开启后不需要设置百度OCR密钥。本地OCR基于PaddleOCR的开源推断模型。  

# 特性及操作说明：  
- 极简窗体无鼠标遮挡  
鼠标可以通过窗体透明的部分点击到后面。  
![image](https://s3.bmp.ovh/imgs/2022/02/35b0bd3b776e5677.png)  
  
- 窗体右下角三个方块  
蓝色点击弹出菜单，黄色按住移动，灰色按住改变大小。  
![image](https://s3.bmp.ovh/imgs/2022/02/4b437f9a429ffd8d.png)  
  
- 鼠标滚轮翻译  
将鼠标悬浮于任意方块处滚动鼠标滚轮即可触发翻译，**不需要窗口焦点**。在支持鼠标滚轮翻页文字的游戏中，**将文字显示速度调到最快即可实现同步翻译**。配置中的文字显示延迟可根据需要调整。**回车键也是内置默认翻译键**，支持回车翻页文字的游戏同理。  
  
- 翻译区域即时修改  
**翻译区域窗体的方块功能与主窗体相同**（没有滚轮翻译和菜单功能）。可进行移动和缩放，将即时改变翻译区域。