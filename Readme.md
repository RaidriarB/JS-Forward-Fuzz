# JS-Forward-Fuzz

Web前端加密场景下的抓包修改、参数模糊测试工具。
本项目基于G-Security-Team的[JS-Forward](https://github.com/G-Security-Team/JS-Forward)二次开发，增加了针对参数进行Fuzz的功能。

## 使用方法

以某金融Web站点的找回密码接口为例。

### （1） 变量转发模式
#### Step 1: 找到变量被加密之前的明文位置

通过分析JS，发现在数据被加密之前，将用户名、手机号、验证码等信息，都存放于`e.data`这个变量之中，且变量的类型是json对象。
![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/1.png)

#### Step 2: 生成能够转发变量的s代码，并插入网页JS中

在工具中按照指引填写信息。

- 首先参数名为上一步发现的`e.data`
- 其次是针对该变量做什么操作，这里先演示变量传递，输入1;
- 最后输入变量类型`json`

![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/2.png)

程序生成了一段代码，接下来通过浏览器的JS Override功能，覆盖网页原本JS。
![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/3.png)

在恰当位置插入程序生成的JS Hook代码。
![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/4.png)

#### Step 3: 程序监听到变量，并发送到BP，可任意修改。

![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/5.png)

![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/6.png)

### （2） Fuzz模式

#### Step 1、Step 2同变量转发模式

只不过在工具中填写信息时，注意针对变量使用FUZZ操作，输入2

#### Step 3: 在fuzz-dict文件夹中构造字典

在文件夹中创建字典文件，假设变量名为`e.data`，那么新建字典文件`e.data.txt`。在字典中每行为一个payload，如果变量类型为string，那么直接放入变量值即可；如果变量类型为json，那么需要复制出json字符串，并在相应位置修改。

![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/7.png)

#### Step 4: 在前端手动点击一次，即可发送一次fuzz请求

去前端页面点击按钮即可，fuzz进度会在`fuzz.progress`中记录，如需充值进度可修改该文件。
![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/8.png)
![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/9.png)