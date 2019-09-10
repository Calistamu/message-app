# Message Filter 垃圾短信过滤APP

## 实施思路
+ Android Studio实现软件显示写好的html页面
+ 点击页面上的按钮读取手机短信，通过API发送到后端服务器；
+ 后端（Python Flask）进行数据处理，返回Json数据给Android Studio前端；
+ Android Studio 前端通过JavaScript将Json数据传给html显示在手机屏幕上
    