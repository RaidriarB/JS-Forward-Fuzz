# JS-Forward-Fuzz

**Web前端加密场景下的参数抓包修改、参数模糊测试工具。**

引用一下工具原作者的介绍：
> 随着互联网安全的发展，对重要的业务系统的安全性要求也在逐渐提升，出现了大量用于加密参数的js，实现了客户端浏览器到服务器直接的参数加密。这个时候想要对渗透测试无疑相当于增加了难度，通常我们F12对其进行调试寻找加密过程密钥，解密参数后修改数据包再加密送往服务器，这个过程繁琐且效率低下，遇到轮询密钥交换等不固定密钥算法时还会更加复杂。
> 
> 为此，Js-Forward被开发了出来，通过使用该工具，可以应对几乎所有的前端加密技术对渗透测试造成的困扰。

本项目基于G-Security-Team的[JS-Forward](https://github.com/G-Security-Team/JS-Forward)二次开发，增加了针对参数进行Fuzz的功能，方便安全测试人员注入SQL、XSS等payload。

## 使用方法
可参考原作者的[文档](https://github.com/G-Security-Team/JS-Forward?tab=readme-ov-file#js-forward-%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95)理解原理，也可以直接看下面的教程。

以某金融Web站点的找回密码接口为例，该接口使用了SM2、SM3、SM4进行对称加密、非对称加密和签名，其中非对称加密的私钥在Web端没有泄漏，通过中间人截获的方式是解不开数据包的，因此只能使用“改内存“大法。

启动工具：`python3 main.py`

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

去前端页面点击按钮即可，fuzz进度会在`fuzz.progress`中记录，如需重置进度可修改该文件。
![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/8.png)
![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/9.png)

## 项目背景
在研究Web前端加密的解决方案时，概括出两条解决路径：基于“中间人”或基于“内存修改”。
首先放一个Web前端加密流程图（不考虑混淆对抗情况）
![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/bg-1.png)

### 路线1：基于中间人的加解密方法

![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/bg-2.png)

方案分析：
- 密码学上，只能破解“能被中间人”的系列
    - 可以破解知道对话密钥的对称加密
    - 非对称加密，若没有服务端私钥，是解不开的
    - 哈希也没办法搞定
- 脚本编写
    - 困难的费劲，要自己写解密逻辑
    - 简单的好办，可以预定义解密逻辑，还是比较简单的
- 集成情况
    - 可作为burp、yakit插件，或者作为下游代理，与其他模块都能配合的比较好。burp能爆破，yakit也能fuzztag，集成情况非常好。
    - 当然，这也是因为它适用的范围有限（只能破解“能被中间人”）的场景。   


方案实例
1. 基于mitmproxy编写脚本，然后burp设置下游代理
2. 编写burp插件，如burpy、jsencrypter
    

  
### 路线2: 在加密之前就截获参数（类似CheatEngine改内存）

我觉得Web这里还不至于像游戏那样有内存数据的交叉检验吧...这个方法应该是更有效的

![](https://raw.githubusercontent.com/RaidriarB/JS-Forward-Fuzz/main/imgs/bg-3.png)

方案分析：

- 密码学上不存在卡脖子情况，任何情况都适用。
- 因为涉及Web APP的修改，可能会遇到反调试等对抗场景。
    - 无限debugger
    - JS混淆
- 脚本编写
    - 不管加解密逻辑困不困难，只要找到位置，“插个眼”，就能解决问题。
    - 关键点在于“插个眼”怎么实现，浏览器有没有好用的机制。
    - “插眼”过程是需要依赖浏览器的，可能要编写浏览器插件，或者自己手动在浏览器里加代码。
- 集成情况
    - 很难集成到burp，因为每次都依赖于实际点击Web APP中的功能键。
    - 不过仅仅是实现fuzz功能的话，倒不用通过burp，还是不难实现的。


方案实例：JSForward，把变量用http请求的方式转发给burp，burp修改后再发回去。相当于用一个web请求进行了hook。这个思路很不错，于是便有了本项目。
