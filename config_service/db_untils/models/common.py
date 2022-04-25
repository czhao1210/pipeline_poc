import sqlite3

sql_script= """
create table if not exists
capi(
    id integer primary key not null,
    seq_num int not null,
    infra text not null,
    sut text not null,
    server
);
create table if not exists
simics(
    id integer primary key,
    seq_num int not null,
    infra text not null,
    sut text not null,
    real_time text,
    serial_port int not null,
    host_name text,
    host_port text,
    host_username text,
    host_password text,
    service_port int,
    os,
    network_user text,
    network_password text,
    app text,
    project text,
    script text
);

create table if not exists
 bmc(
    id integer primary key,
    seq_num int not null,
    infra text not null,
    sut text not null,
    ip text not null,
    port text not null,
    username text not null,
    password text not null    
);

create table if not exists
 ssh(
    id integer primary key,
    seq_num int not null,
    infra text not null,
    sut text not null,
    hostname text not null,
    port text not null,
    username text not null,
    password text not null    
);

create table  if not exists
pdu(
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

create table if not exists
impl(
    id integer primary key,
    config_name text not null,
    infra text,
    provider_name text not null,
    label text,
    use text not null,
    parameters text   
);

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
        self.__cur.executescript(sql_script)
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

    def suggest_id(self, table_name):
        sql = f"""
        select max(id) as max_id from {table_name};
        """
        ret = self.query(sql)
        return ret[0]["max_id"] + 1 if ret[0]["max_id"] is not None else 1

    def filter_impl(self, config_name, infra):
        sql = f"""
        select * from impl
        where config_name="{config_name}" and infra="{infra}" order by provider_name asc;
        """
        ret = self.query(sql)
        return ret if ret else list()

    def remove_generic(self, table_name, **kwargs):
        where_clause = list()
        for k, v in kwargs.items():
            if isinstance(v, str):
                where_clause.append(f"{k}=\"{v}\"")
            elif v is not None:
                where_clause.append(f"{k}={v}")
        if where_clause:
            sql = f"""
            DELETE FROM {table_name}
            WHERE {" AND ".join(where_clause)};
            """
        else:
            sql = f"""
            DELETE FROM {table_name};
            """
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
            values.append(v)

        sql = f"""
        INSERT INTO {type(data_model).__name__.lower()} ({",".join(keys)}) VALUES ({",".join("?"*len(values))});
        """
        try:
            self.__cur.execute(sql, values)
        except sqlite3.OperationalError as ex:
            print(f"ex={ex},sql={sql}")

    def remove(self, data_model):
        sql = f"""
        DELETE FROM {type(data_model).__name__.lower()} WHERE id={data_model.id};
        """
        self.__cur.execute(sql)

