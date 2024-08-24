import sqlite3

class Integer:
    pass

class String:
    def __init__(self, length=255):
        self.length = length

class Varchar:
    def __init__(self, length=255):
        self.length = length

class Text:
    pass

class Boolean:
    pass

class Date:
    pass

class Timestamp:
    pass

class Real:
    pass

class Table:
    def __init__(self, name, connection):
        self.name = name
        self.connection = connection
        self.cursor = connection.cursor()
        self.columns_definitions = []
        self.unique_columns = []
        self.table_created = self.check_table_exists()

    def check_table_exists(self):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.name}'")
        return bool(self.cursor.fetchone())

    def columns(self, name, column_type, **options):
        if self.table_created:
            return

        column_def = [name]

        if isinstance(column_type, Integer):
            if options.get('auto_increment', False):
                column_def.append('INTEGER PRIMARY KEY AUTOINCREMENT')
            else:
                column_def.append('INTEGER')
        elif isinstance(column_type, String):
            column_def.append(f'VARCHAR({column_type.length})')
        elif isinstance(column_type, Varchar):
            column_def.append(f'VARCHAR({column_type.length})')
        elif isinstance(column_type, Text):
            column_def.append('TEXT')
        elif isinstance(column_type, Boolean):
            column_def.append('BOOLEAN')
        elif isinstance(column_type, Date):
            column_def.append('DATE')
        elif isinstance(column_type, Timestamp):
            column_def.append('TIMESTAMP')
        elif isinstance(column_type, Real):
            column_def.append('REAL')
        else:
            column_def.append('TEXT')

        if options.get('not_null', False):
            column_def.append('NOT NULL')
        if options.get('unique', False):
            column_def.append('UNIQUE')
            self.unique_columns.append(name)
        if 'default' in options:
            column_def.append(f"DEFAULT {options['default']}")

        self.columns_definitions.append(' '.join(column_def))
        return self

    def create(self):
        if not self.table_created:
            columns_with_types = ', '.join(self.columns_definitions)
            create_table_query = f"CREATE TABLE IF NOT EXISTS {self.name} ({columns_with_types})"
            print(f"Running query: {create_table_query}")
            self.cursor.execute(create_table_query)
            self.connection.commit()
            self.table_created = True

    def add(self, **kwargs):
        if self.unique_columns:
            unique_check_conditions = {col: kwargs[col] for col in self.unique_columns if col in kwargs}
            if unique_check_conditions:
                existing_record = self.select(where=unique_check_conditions)
                if existing_record:
                    print(f"Record with unique values {unique_check_conditions} already exists. Skipping insert.")
                    return

        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' * len(kwargs))
        values = tuple(kwargs.values())
        insert_query = f"INSERT INTO {self.name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(insert_query, values)
        self.connection.commit()

    def select(self, where=None, like=None, order_by=None, order_direction='ASC'):
        query = f"SELECT * FROM {self.name}"
        parameters = []

        if where:
            conditions = ' AND '.join([f"{k} = ?" for k in where.keys()])
            query += f" WHERE {conditions}"
            parameters.extend(where.values())

        if like:
            like_conditions = ' AND '.join([f"{k} LIKE ?" for k in like.keys()])
            if 'WHERE' in query:
                query += f" AND {like_conditions}"
            else:
                query += f" WHERE {like_conditions}"
            parameters.extend(like.values())

        if order_by:
            query += f" ORDER BY {order_by} {order_direction}"

        self.cursor.execute(query, parameters)
        results = self.cursor.fetchall()

        column_names = [description[0] for description in self.cursor.description]
        return [dict(zip(column_names, row)) for row in results]

    def select_join(self, other_table, fields='*', on=None, where=None, like=None, order_by=None, order_direction='ASC'):
        if fields == '*':
            fields = f"{self.name}.*, {other_table}.*"
        else:
            fields = ', '.join(fields)

        query = f"SELECT {fields} FROM {self.name} JOIN {other_table} ON {on}"

        parameters = []

        if where:
            conditions = []
            for k, v in where.items():
                if isinstance(v, tuple):
                    operator, value = v
                    conditions.append(f"{k} {operator} ?")
                    parameters.append(value)
                else:
                    conditions.append(f"{k} = ?")
                    parameters.append(v)

            query += f" WHERE {' AND '.join(conditions)}"

        if like:
            like_conditions = ' AND '.join([f"{k} LIKE ?" for k in like.keys()])
            if 'WHERE' in query:
                query += f" AND {like_conditions}"
            else:
                query += f" WHERE {like_conditions}"
            parameters.extend(like.values())

        if order_by:
            query += f" ORDER BY {order_by} {order_direction}"

        print(f"Running query: {query}")
        self.cursor.execute(query, parameters)
        results = self.cursor.fetchall()

        column_names = [description[0] for description in self.cursor.description]
        return [dict(zip(column_names, row)) for row in results]

    def delete(self, **kwargs):
        if kwargs:
            condition = ' AND '.join([f"{k} = ?" for k in kwargs.keys()])
            delete_query = f"DELETE FROM {self.name} WHERE {condition}"
            self.cursor.execute(delete_query, tuple(kwargs.values()))
        else:
            delete_query = f"DELETE FROM {self.name}"
            self.cursor.execute(delete_query)
        self.connection.commit()

    def update(self, where_clause, **new_values):
        update_clause = ', '.join([f"{k} = ?" for k in new_values.keys()])
        condition = ' AND '.join([f"{k} = ?" for k in where_clause.keys()])
        update_query = f"UPDATE {self.name} SET {update_clause} WHERE {condition}"
        self.cursor.execute(update_query, tuple(new_values.values()) + tuple(where_clause.values()))
        self.connection.commit()


class Database:
    def __init__(self, db_name=':memory:'):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.tables = {}

    def table(self, name):
        if name not in self.tables:
            self.tables[name] = Table(name, self.connection)
        return self.tables[name]

    def close(self):
        self.connection.close()
