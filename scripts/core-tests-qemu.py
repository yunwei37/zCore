import pexpect
import sys
import time
import os
import re
import multiprocessing

TIMEOUT = 10
ZCORE_PATH = '../zCore'
OUTPUT_FILE = 'test-output.txt'
RESULT_FILE = 'test-result.txt'
STATISTIC_FILE = 'test-statistic.txt'
CHECK_FILE = 'test-check-passed.txt'
TEST_CASE_FILE = 'testcases.txt'
ALL_CASES = 'all-test-cases.txt'

PROCESSES = 10
PREBATCH = 3

IMG = '../zCore/target/x86_64/release/disk.qcow2'
ESP = '../zCore/target/x86_64/release/esp'



class Tee:
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self

    def __del__(self):
        sys.stdout = self.stdout
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        self.file.flush()

def qcow2_duplication(num):
    if not os.path.exists("../zCore/target/x86_64/release/disk/"):
        print("disk 文件夹不存在")
        os.system("mkdir ../zCore/target/x86_64/release/disk/")
        print("disk 创建完毕")
    print("qcow2 copying...")
    for i in range(0,PREBATCH):
        for j in range(0,num):
            os.system("cp "+IMG+" ../zCore/target/x86_64/release/disk/disk"+str(i)+"_"+str(j)+".qcow2")
    print("qcow2 copying...finished")

def esp_duplication(num):
    print("esp copying...")
    for i in range(0,num):
        os.system("cp -r "+ESP+" ../zCore/target/x86_64/release/esp"+str(i))
    
    print("esp copying...finished")

def running(index_num,line):
    line = line.strip()
    i = index_num%PROCESSES
    batch = int(index_num/PROCESSES)%PREBATCH
    print('[running]    '+str(index_num)+'    '+line)
    write_arg(i,line)

    child = pexpect.spawn("qemu-system-x86_64 \
                                -smp 1 -machine q35 \
                                -cpu Haswell,+smap,-check,-fsgsbase \
                                -drive if=pflash,format=raw,readonly,file=../rboot/OVMF.fd \
                                -drive format=raw,file=fat:rw:../zCore/target/x86_64/release/esp"+str(i)+" \
                                -drive format=qcow2,file=../zCore/target/x86_64/release/disk/disk"+str(batch)+"_"+str(i)+".qcow2,id=disk,if=none \
                                -device ich9-ahci,id=ahci \
                                -device ide-drive,drive=disk,bus=ahci.0 \
                                -serial mon:stdio -m 4G -nic none \
                                -device isa-debug-exit,iobase=0xf4,iosize=0x04 \
                                -display none -nographic",
                                timeout=TIMEOUT, encoding='utf-8')
                                # -accel kvm -cpu host,migratable=no,+invtsc  \ kvm 把这个加上

    index = child.expect(['PASSED','FAILED','panicked', pexpect.EOF, pexpect.TIMEOUT,'Running 0 test from 0 test case'])
    result = ['PASSED','FAILED','PANICKED', 'EOF', 'TIMEOUT','UNKNOWN'][index]
    print('[result]    '+str(index_num)+'    '+line+'    '+result)
    with open(RESULT_FILE, "a") as f:
        f.write('[result]    '+str(index_num)+'    '+line+'    '+result+'\n')

def write_arg(index,line,):
    content=[]
    with open("../zCore/target/x86_64/release/esp"+str(index)+"/EFI/Boot/rboot.conf","r") as f:
        content = f.readlines()
    i=0
    while i < len(content):
        if content[i].startswith("cmdline"):
            content[i] = "cmdline=LOG=warn:userboot=test/core-standalone-test:userboot.shutdown:core-tests="+line
        i = i + 1
    with open("../zCore/target/x86_64/release/esp"+str(index)+"/EFI/Boot/rboot.conf","w") as f:
        f.writelines(content)


lines = []
with open(ALL_CASES, "r") as f:
    lines = f.readlines()

with open(RESULT_FILE, "w") as f:
    f.write('测例统计:\n')

qcow2_duplication(PROCESSES)
esp_duplication(PROCESSES)

pool = multiprocessing.Pool(processes = PROCESSES)
start = time.time() 
print("开始计时")
for (n,line) in enumerate(lines):
    if line.startswith('#') or line.startswith('\n'):
        continue

    pool.apply_async(running,(n,line,))

pool.close()
pool.join()   #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
end = time.time()
print('用时--times{:.3f}'.format(end-start))

os.system('python3 diff.py')