## 基于sql-lab的bool盲注脚本

> 作者：libestor

基于sql-labs 第五关的盲注爆破脚本

使用方法与sqlmap类似，可以通过-h查看详细情况

> 输入的url是已经绕过但引号的url，由于无法输入单引号，所以需要用%27代替但引号

​	例如：python main.py -u example.com/?id=1 %27  --databases

### 优点

* 查询使用了**折半查找**可以提高一点点速度
* 查询有着比较好的**错误提示**，方便查看问题所在
* 数据都可以保存为json文件，方便使用和回溯
* 很多查询语句都已经写成了注释，方便学习

### 不足点

* 判断条件没有模块化，使得函数在其他地方使用的时候不好修改，（说人话，移植性差）

* 数据输入必须按照顺序，必须是先-D  <database>  -T <tables>   -C   <column> 这样的顺序，不然会出现问题

### 改进点

* 可以使用多个线程处理加快速度

联系作者：443318033@qq.com

