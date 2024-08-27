from datetime import datetime
from io import StringIO
import pandas as pd
import peewee
from peewee import (
    Model, CharField, DateTimeField,
    ForeignKeyField, ModelSelect,
)
from playhouse.migrate import migrate, PostgresqlMigrator
from playhouse.postgres_ext import PostgresqlExtDatabase, JSONField
from playhouse.shortcuts import model_to_dict
from tqdm import tqdm
from docketanalyzer import (
    POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT, 
    POSTGRES_PASSWORD, POSTGRES_USERNAME,
)


class CustomQueryMixin:
    def pandas(self, *columns, copy=False):
        if columns:
            columns = [getattr(self.model, col) for col in columns]
            query = self.select(*columns)
        else:
            query = self

        if copy:
            conn = self.model._meta.database.connection()
            with conn.cursor() as cursor:
                sql, params = query.sql()
                params = tuple(params) if isinstance(params, list) else params
                copy_sql = cursor.mogrify(
                    f"COPY ({sql}) TO STDOUT WITH CSV HEADER", 
                    params,
                ).decode('utf-8')
                buffer = StringIO()
                cursor.copy_expert(copy_sql, buffer)
                buffer.seek(0)
                data = pd.read_csv(buffer)
        else:
            data = pd.DataFrame(list(query.dicts()))

        return data

    def sample(self, n):
        return self.order_by(peewee.fn.Random()).limit(n)

    def delete(self):
        model_class = self.model
        subquery = self.select(model_class._meta.primary_key)
        delete_query = model_class.delete().where(
            model_class._meta.primary_key.in_(subquery)
        )
        return delete_query.execute()

    def batch(self, n, verbose=True):
        model_class = self.model
        pk_field = model_class._meta.primary_key
        query = self.clone()
        query = query.order_by(pk_field)
        total, progress = None, None

        if verbose:
            total = query.count()
            progress = tqdm(total=total)

        last_id, processed = None, 0
        while True:
            if last_id is not None:
                batch_query = query.where(pk_field > last_id)
            else:
                batch_query = query

            batch = batch_query.limit(n)
            if not batch:
                break
            yield batch

            last_id = getattr(batch[-1], pk_field.name)
            processed += len(batch)
            if verbose:
                progress.update(len(batch))
        if verbose:
            progress.close()


class CustomModelSelect(ModelSelect, CustomQueryMixin):
    pass


class CustomModel(Model):
    @classmethod
    def select(cls, *fields):
        return CustomModelSelect(cls, fields)

    @classmethod
    def sample(cls, n):
        return cls.select(cls).sample(n)
    
    @classmethod
    def pandas(cls, *columns, copy=False):
        return cls.select(cls).pandas(*columns, copy=copy)

    @classmethod
    def where(cls, *args, **kwargs):
        return cls.select(cls).where(*args, **kwargs)

    @classmethod
    def batch(cls, n, verbose=False):
        return cls.select(cls).batch(n, verbose=verbose)

    @classmethod
    def drop_column(self, column_name):
        migrator = PostgresqlMigrator(self._meta.database)
        table_name = self._meta.table_name
        T, C = self.t.T, self.t.C
        confirm = input(f'Are you sure you want to overwrite column {column_name} in table {table_name}?\nThis will DELETE ALL COLUMN DATA.\n(y/n): ')
        if not confirm == 'y': 
            print('Aborted.')
            return
        try:
            migrate(
                migrator.drop_column(table_name, column_name)
            )
        except peewee.ProgrammingError as e:
            print(e)
        column = C.get(C.name == column_name)
        column.delete_instance()
        self.t.reload()

    @classmethod
    def add_column(self, column_name, column_type, null=True, overwrite=False, **kwargs):
        migrator = PostgresqlMigrator(self._meta.database)
        table_name = self._meta.table_name
        T, C = self.t.T, self.t.C
        if table_name not in self.t:
            T.create(name=table_name)
        columns = C.select().join(T).where(T.name == table_name)
        if column_name in [x.name for x in columns]:
            if not overwrite:
                return
            self.drop_column(column_name)
        table = T.get(T.name == table_name)
        kwargs['null'] = null
        migrate(
            migrator.add_column(table_name, column_name, getattr(peewee, column_type)(**kwargs))
        )
        C.create(table=table, name=column_name, type=column_type, args=kwargs)
        self.t.reload()
    
    @classmethod
    def add_data(cls, data, copy=False):
        if copy:
            conn = cls._meta.database.connection()
            with conn.cursor() as cursor:
                buffer = StringIO()
                data.to_csv(buffer, index=False, header=False)
                buffer.seek(0)
                cursor.copy_from(buffer, cls._meta.table_name, sep=',', columns=data.columns)
        else:
            data = data.to_dict(orient='records')
            with cls._meta.database.atomic():
                for batch in chunked(data, 100):
                    cls.insert_many(batch).execute()
    
    def dict(self):
        return model_to_dict(self)

    @classmethod
    def count(cls):
        return cls.select().count()


class Tables:
    def __init__(self, db, T, C):
        self.db = db
        self.T = T
        self.C = C
        self.tables = {}

    def get_table_class(self, name):
        class Meta:
            database = self.db
            table_name = name
        
        attrs = {'Meta': Meta}
        columns = self.C.select().join(self.T).where(self.T.name == name)
        for column in columns:
            field_type = getattr(peewee, column.type)
            attrs[column.name] = field_type(**column.args)

        TableClass = type(name, (CustomModel,), attrs)
        TableClass.t = self
        self.db.create_tables([TableClass])
        return TableClass
    
    def reload(self):
        tables = self.T.select()
        for table in tables:
            self.tables[table.name] = self.get_table_class(table.name)

    def __contains__(self, name):
        return name in self.tables

    def __getitem__(self, name):
        try:
            return self.tables[name]
        except KeyError:
            raise KeyError(f'Table {name} does not exist. Use db.create_table to create it.')
    
    def __getattr__(self, name):
        return self[name]


class Database:
    def __init__(self, db_name=POSTGRES_DB, host=POSTGRES_HOST, port=POSTGRES_PORT, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD):
        self.db = PostgresqlExtDatabase(
            db_name, 
            host=host, port=port,
            user=user, password=password,
        )
        self.t = None
        self.T = None
        self.C = None
        self.init()
    
    def init(self):
        db = self.db

        class Table(Model):
            name = CharField(unique=True)
            created = DateTimeField(default=datetime.now)
            data = JSONField(default={})
            
            class Meta:
                database = db
                indexes = (
                    (('name',), True),
                )

        class Column(Model):
            table = ForeignKeyField(Table)
            name = CharField()
            type = CharField()
            args = JSONField(default={})
            created = DateTimeField(default=datetime.now)
            data = JSONField(default={})

            class Meta:
                database = db
                indexes = (
                    (('table', 'name'), True),
                )
        
        self.T = Table
        self.C = Column
        db.create_tables([Table, Column])
        self.t = Tables(self.db, self.T, self.C)
        self.t.reload()
    
    def create_table(self, name, exists_ok=True):
        if name in self.t:
            if not exists_ok:
                raise ValueError(f'Table {name} already exists.')
            return
        self.T.insert(name=name).execute()
        self.t.reload()


def connect(database=POSTGRES_DB, host=POSTGRES_HOST, port=POSTGRES_PORT, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD):
    return Database(database, host, port, user, password)
