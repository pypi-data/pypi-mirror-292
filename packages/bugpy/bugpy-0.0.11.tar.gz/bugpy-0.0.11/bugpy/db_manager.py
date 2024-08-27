import mysql.connector
import numpy as np
import pandas as pd
from pandas import read_sql
from bugpy.utils import SqlFormatter
import warnings

pd.options.mode.chained_assignment = None

warnings.filterwarnings('ignore','.*SQLAlchemy.*')

class Connection:
    def __init__(self, user, password, host, database):
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        self.db = None
        self.cursor = None
        self.connect()

    def connected(self):
        if self.db is None:
            return False
        if self.db.is_connected():
            return True
        return False

    def close(self):
        try:
            self.db.close()
            return True
        except Exception as e:
            print(e)
            return False

    def commit(self):
        if not self.connected():
            self.connect()
        self.db.commit()

    def connect(self, force_reconnect=False) -> bool:
        if not force_reconnect:
            if self.connected():
                return True
        try:
            if self.connected():
                self.close()
            self.db = mysql.connector.connect(host=self.host, database=self.database, user=self.user, passwd=self.password, use_pure=True)
            self.cursor = self.db.cursor()
            return True
        except mysql.connector.Error as err:
            raise PermissionError(f"Could not connect to MySQL database, reason: {err}")
        except Exception as e:
            print(e)
            return False

    def query(self, query:str, retries = 1) -> pd.DataFrame:
        if not self.connected():
            self.connect()
        success = False
        for i in range(retries+1):
            try:
                output_df = read_sql(query, self.db)
                success = True
                break
            except mysql.connector.errors.DatabaseError as e:
                error = e
        if not success:
            raise Exception(str(error))

        return output_df

    def _format_df(self, dataframe: pd.DataFrame, table: str, include_autokey=False) -> pd.DataFrame:
        """Formats a dataframe to align it with a given database table"""

        fmt = SqlFormatter(table, include_autokey, self)

        dataframe = fmt.format(dataframe)

        return dataframe

    def _generate_insert_query(self, df, table):
        df = self._format_df(df, table)
        df = df.drop_duplicates()
        query = f"INSERT INTO {table} ({','.join([col for col in df])}) VALUES "
        for i, row in df.iterrows():
            query += '('+','.join([row[col] for col in df]) + '),'
        query = query[:-1]
        return query

    def insert(self, df: pd.DataFrame, table:str, batch_size=10000, retries=1):
        if len(df)==0:
            print("Dataframe is empty!")
            return False
        records = 0
        if not self.connected():
            self.connect()
        for i in np.arange(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            query = self._generate_insert_query(batch, table)
            success = False
            for j in range(retries+1):
                try:
                    self.cursor.execute(query)
                    success=True
                    break
                except mysql.connector.errors.DatabaseError as e:
                    error = e
            if not success:
                raise Exception(error.__str__())
            records = records + self.cursor.rowcount

        self.commit()
        print(f'{records} records inserted')

        return True


    def callproc(self, sp, args=None, num_outputs=0, output_table=None, commit=None, retries=0):
        """ Calls a stored procedure

            :param sp: the name of the stored procedure
            :type sp: str
            :param args: the input arguments for the stored procedure
            :param num_outputs: the number of outputs of the stored procedure, defaults to 0
            :type num_outputs: int
            :param output_table: the name of the table where any expected outputs are stored, defaults to None
            :type output_table: str
            :param commit: whether the result of the stored procedure should be committed
            :type commit: bool
            :param retries: number of time to retry process before giving up, defaults to 0
        """
        if args is None:
            args = []
        if commit is None:
            commit = self.commit

        if not self.connected():
            self.connect()

        if type(args) != list:
            args = [args]

        input_args = args

        success = False
        result = []
        result_table = pd.DataFrame()
        error = InvalidValue("retries must be greater than or equal to 0")
        for i in range(retries + 1):
            try:
                args = input_args + ['0'] * num_outputs
                result = list(self.cursor.callproc(sp, args))[-num_outputs:]
                if output_table is not None:
                    result_table = self.query(f"SELECT * FROM {output_table}")
                success = True
                break
            except mysql.connector.errors.DatabaseError as e:
                error = DatabaseError(e.__str__())
            except mysql.connector.errors.InterfaceError as e:
                error = DatabaseError(e.__str__())
            except Exception as e:
                error = e
        if not success:
            raise error

        if len(result) == 1:
            result = result[0]

        if commit:
            self.commit_to_db()

        if output_table:
            if num_outputs == 0:
                return result_table
            else:
                return result, result_table
        return result