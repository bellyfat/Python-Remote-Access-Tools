import os


path = raw_input('Input file path: ')
fname = os.path.basename(path)
fsize = os.path.getsize(path)
print fsize

print(isize)
if os.path.isfile(path):
    try:
        with open(path) as f:
            data = f.read(isize)
            print str(len(data))
            print str(len(fsize))
        recvfile = open('test', 'w')
        recvfile.write(data)
    except IOError:
        print('Error: Permission denied.')
else:
    print('Error: File not found.')
