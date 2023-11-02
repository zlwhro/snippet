def fill_file_with_a(filename, index):
    file = open(filename, mode='rb')
    content = file.read()
    with open(filename+'.jpg', 'wb') as f:
        f.write(content)
        f.seek(0)
        f.write(b'\xff')
        f.write(b'\xd8')
        f.write(b'\xff')
        f.write(b'=')

        f.write(b'\x09')
        f.write(b'\x09')


        f.seek(0, 2)  # 파일 끝으로 이동
        file_size = f.tell()  # 현재 파일 크기 확인

        if file_size < index:
            remaining_bytes = index- file_size +2
            f.write(b"/*"+b'\x20' * remaining_bytes)
            print(f"파일 끝에 {remaining_bytes}바이트의 공백 채워졌습니다.")
        else:
            print(f"파일 크기가 {index}바이트보다 크거나 같습니다.")
        print(f.tell())
        f.write(b'\xff')
        f.write(b'\xc0')

        # i+2~4
        f.write(b'\x20')
        f.write(b'\x20')
        f.write(b'\x20')

        # height
        f.write(b'\x09')
        f.write(b'\x09')

        # width
        f.write(b'\x09')
        f.write(b'\x09')
        f.write(b'*/')

javasciprt_file = 'test.js'
fill_file_with_a(javascript_file,0x909)
