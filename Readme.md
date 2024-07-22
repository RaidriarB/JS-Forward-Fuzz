# JS-Forward-Fuzz

Web前端加密场景下的抓包修改、参数模糊测试工具。
本项目基于G-Security-Team的[JS-Forward](https://github.com/G-Security-Team/JS-Forward)二次开发，增加了针对参数进行Fuzz的功能。

## 使用方法

以某金融Web站点为例。

### Step 1: 找到变量被加密之前的明文位置

通过分析JS，发现该站点中数据被加密之前，存放于`e.data`这个变量之中，并且变量的类型是json对象。

### Step 2: 生成能够转发变量的js代码，并插入网页JS中


### Step 3: 程序监听到变量，并发送到BP，可任意修改。
