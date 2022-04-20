import sqlite3

sql_script= """
create table capi(
    id integer primary key not null,
    infra text not null,
    sut text not null,
    server
);
insert into capi values(1, "emr-capi", "sut0", "capi_server_url");

create table simics(
    id integer primary key,
    infra, 
    host_address
);
insert into simics values(1, "simcloud", "host_addr0");

create table bmc(
    id integer primary key,
    seq_num int not null,
    infra text not null,
    sut text not null,
    ip text not null,
    port text not null,
    username text not null,
    password text not null    
);
insert into bmc values(1,0, "emr", "sut0", "127.0.0.1", "5000", "user", "password");

create table pdu(
    id integer primary key,
    seq_num int not null,
    infra text not null,
    sut text not null,
    ip text not null,
    port text not null,
    username text not null,
    password text not null,
    outlets text not null,
    type text not null    
);
insert into pdu values(1, 0, "emr", "sut0", "0.0.0.0", "22", "user", "password", "10, 11, 12","raritan");
insert into pdu values(2, 1, "emr", "sut0", "0.0.0.0", "22", "user", "password", "20,21","raritan");

"""

class Connection(object):
    def __init__(self) -> None:
        super().__init__()

    def __enter__(self):
        """
        Enter resource context for this Provider.

        :return: Resource to use (usually self)
        """
        #self.__con = sqlite3.connect(r":memory:")
        self.__con = sqlite3.connect(r"config.db")
        self.__cur = self.__con.cursor()
        #self.__cur.executescript(sql_script)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit resource context for this Provider.

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        """
        self.__con.close()

    def query(self, sql):
        results = self.__cur.execute(sql).fetchall()
        values = list()
        for ret in results:
            v = dict()
            for idx, col in enumerate(self.__cur.description):
                v[col[0]] = ret[idx]
            if v:
                values.append(v)
        return values

    def get_device(self, infra, sut, device):
        sql = f"""
        select * from {device}
        where sut="{sut}" and infra="{infra}";
        """
        ret = self.query(sql)
        return ret[0] if ret else None

    def dump(self, table):
        sql = f"select * from {table};"
        ret = self.query(sql)
        return ret if ret else list()


    def filter_device(self, infra, sut, device):
        sql = f"""
        select * from {device}
        where sut="{sut}" and infra="{infra}" order by seq_num asc;
        """
        ret = self.query(sql)
        return ret if ret else list()

    def commit(self):
        self.__con.commit()

    def revert(self):
        self.__con.rollback()

    def update(self, data_model):
        value_list = list()
        for k, v in data_model.data.items():
            if isinstance(v, str) and k != "id":
                value_list.append(f"{k}=\"{v}\"")
            elif k != "id":
                value_list.append(f"{k}={v}")
        sql = f"""
        update {type(data_model).__name__.lower()} set {",".join(value_list)} where id = {data_model.id};
        """
        self.__cur.execute(sql)
        ret = self.query("select * from pdu;")
        return ret if ret else list()

    def add(self, data_model):
        keys = list()
        values = list()
        for k, v in data_model.data.items():
            keys.append(k)
            if isinstance(v, str):
                values.append(f"\"{v}\"")
            else:
                values.append(f"{v}")
        sql = f"""
        INSERT INTO {type(data_model).__name__.lower()} ({",".join(keys)}) VALUES ({",".join(values)});
        """
        try:
            self.__cur.execute(sql)
        except sqlite3.OperationalError as ex:
            print(f"ex={ex},sql={sql}")

    def remove(self, data_model):
        sql = f"""
        DELETE FROM {type(data_model).__name__.lower()} WHERE id={data_model.id};
        """
        self.__cur.execute(sql)

