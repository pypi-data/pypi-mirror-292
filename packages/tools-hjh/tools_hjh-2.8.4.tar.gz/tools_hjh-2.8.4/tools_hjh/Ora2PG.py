# coding:utf-8
from tools_hjh.DBConn import DBConn
from tools_hjh import Tools
from tools_hjh import Log

date = Tools.locatdate()
log = Log('' + date + '.log')


def main():
    pass


class Ora2PG:

    @staticmethod
    def move_table_data(ora_db, pg_db, src_owner, src_table, dst_owner, dst_table, sct_scn):
        pass
    
    @staticmethod
    def build_meta_data(ora_db, owner, commit_num=100000):
        scn = ora_db.run('select to_char(current_scn) from v$database').get_rows()[0][0]
        meta_db = DBConn('sqlite', db='meta_data/' + owner + '_' + scn + '.db')
        tables = ora_db.run("select table_name from dba_tables where owner = ?", (owner.upper(),)).get_rows()
        for table in tables:
            table_name = table[0]
            create_sql = 'create table ' + table_name + ' if not exists(rowid char(18), status char(1))'
            select_sql = 'select rowid from ' + owner + '.' + table_name + ' as of scn ' + scn
            insert_sql = 'insert into ' + table_name + '(rowid) values(?)'
            meta_db.run(create_sql)
            cur = ora_db.run(select_sql).get_rows_2()
            insert_params = []
            i = 0
            insert_num = 0
            for row in cur:
                i = i + 1
                insert_params.append((row[0]))
                if i == commit_num:
                    meta_db.run(insert_sql, insert_params)
                    insert_num = insert_num + insert_params.clear()
            if len(insert_params) > 0:
                meta_db.run(insert_sql, insert_params)
                insert_num = insert_num + insert_params.clear()
                
            log.info('build_meta_data', table_name, insert_num)
       
    @staticmethod    
    def copy_table_data(ora_db, pg_db, src_owner, src_table, dst_owner, dst_table):
        select_sql = 'select * from ' + src_owner + '.' + src_table
        rs = ora_db.run(select_sql)
        s = ''
        for i in range(0, rs.get_cols()):
            s = s + '?,'
        s = s.strip(',')
        insert_sql = 'insert into ' + dst_owner + '.' + dst_table + ' values(' + s + ')'

    
if __name__ == '__main__':
    main()
