import argparse
import psutil
import redis
import time
import datetime
import sys
import ctypes
import subprocess
import GPUtil

ACCESS_DENIED = ''

CUDA_SUCCESS = 0
CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT = 16
CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_MULTIPROCESSOR = 39
CU_DEVICE_ATTRIBUTE_CLOCK_RATE = 13
CU_DEVICE_ATTRIBUTE_MEMORY_CLOCK_RATE = 36

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def ConvertSMVer2Cores(major, minor):
    # Returns the number of CUDA cores per multiprocessor for a given
    # Compute Capability version. There is no way to retrieve that via
    # the API, so it needs to be hard-coded.
    return {(1, 0): 8,
            (1, 1): 8,
            (1, 2): 8,
            (1, 3): 8,
            (2, 0): 32,
            (2, 1): 48,
            }.get((major, minor), 192)  # 3.0 and above

def cuda_info():
    libnames = ('libcuda.so', 'libcuda.dylib', 'cuda.dll')
    for libname in libnames:
        try:
            cuda = ctypes.CDLL(libname)
        except OSError:
            continue
        else:
            break
    else:
        raise OSError("could not load any of: " + ' '.join(libnames))

    nGpus = ctypes.c_int()
    name = b' ' * 100
    cc_major = ctypes.c_int()
    cc_minor = ctypes.c_int()
    cores = ctypes.c_int()
    threads_per_core = ctypes.c_int()
    clockrate = ctypes.c_int()
    freeMem = ctypes.c_size_t()
    totalMem = ctypes.c_size_t()

    result = ctypes.c_int()
    device = ctypes.c_int()
    context = ctypes.c_void_p()
    error_str = ctypes.c_char_p()

    result = cuda.cuInit(0)
    if result != CUDA_SUCCESS:
        cuda.cuGetErrorString(result, ctypes.byref(error_str))
        print("cuInit failed with error code %d: %s" % (result, error_str.value.decode()))
        return 1
    result = cuda.cuDeviceGetCount(ctypes.byref(nGpus))
    if result != CUDA_SUCCESS:
        cuda.cuGetErrorString(result, ctypes.byref(error_str))
        print("cuDeviceGetCount failed with error code %d: %s" % (result, error_str.value.decode()))
        return 1
    print("Found %d cuda device(s)." % nGpus.value)
    for i in range(nGpus.value):
        result = cuda.cuDeviceGet(ctypes.byref(device), i)
        if result != CUDA_SUCCESS:
            cuda.cuGetErrorString(result, ctypes.byref(error_str))
            print("cuDeviceGet failed with error code %d: %s" % (result, error_str.value.decode()))
            return 1
        print("Device: %d" % i)
        if cuda.cuDeviceGetName(ctypes.c_char_p(name), len(name), device) == CUDA_SUCCESS:
            print("  Name: %s" % (name.split(b'\0', 1)[0].decode()))
        if cuda.cuDeviceComputeCapability(ctypes.byref(cc_major), ctypes.byref(cc_minor), device) == CUDA_SUCCESS:
            print("  Compute Capability: %d.%d" % (cc_major.value, cc_minor.value))
        if cuda.cuDeviceGetAttribute(ctypes.byref(cores), CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT, device) == CUDA_SUCCESS:
            print("  Multiprocessors: %d" % cores.value)
            print("  CUDA Cores: %d" % (cores.value * ConvertSMVer2Cores(cc_major.value, cc_minor.value)))
            if cuda.cuDeviceGetAttribute(ctypes.byref(threads_per_core), CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_MULTIPROCESSOR, device) == CUDA_SUCCESS:
                print("  Concurrent threads: %d" % (cores.value * threads_per_core.value))
        if cuda.cuDeviceGetAttribute(ctypes.byref(clockrate), CU_DEVICE_ATTRIBUTE_CLOCK_RATE, device) == CUDA_SUCCESS:
            print("  GPU clock: %g MHz" % (clockrate.value / 1000.))
        if cuda.cuDeviceGetAttribute(ctypes.byref(clockrate), CU_DEVICE_ATTRIBUTE_MEMORY_CLOCK_RATE, device) == CUDA_SUCCESS:
            print("  Memory clock: %g MHz" % (clockrate.value / 1000.))
        result = cuda.cuCtxCreate(ctypes.byref(context), 0, device)
        if result != CUDA_SUCCESS:
            cuda.cuGetErrorString(result, ctypes.byref(error_str))
            print("cuCtxCreate failed with error code %d: %s" % (result, error_str.value.decode()))
        else:
            result = cuda.cuMemGetInfo(ctypes.byref(freeMem), ctypes.byref(totalMem))
            if result == CUDA_SUCCESS:
                print("  Total Memory: %ld MiB" % (totalMem.value / 1024**2))
                print("  Free Memory: %ld MiB" % (freeMem.value / 1024**2))
            else:
                cuda.cuGetErrorString(result, ctypes.byref(error_str))
                print("cuMemGetInfo failed with error code %d: %s" % (result, error_str.value.decode()))
            cuda.cuCtxDetach(context)
    return 0

rs = redis.StrictRedis(port=6379, host='localhost')
pid = rs.get('pid_to_monitor')

def convert_bytes(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

def str_ntuple(nt, bytes2human=False):
    if nt == ACCESS_DENIED:
        return ""
    if not bytes2human:
        return ", ".join(["%s=%s" % (x, getattr(nt, x)) for x in nt._fields])
    else:
        return ", ".join(["%s=%s" % (x, convert_bytes(getattr(nt, x)))
                          for x in nt._fields])

def gpu_mem(pid):
	cmd="nvidia-smi | awk '$3=="+str(pid)+" {print $6}'"
	sp = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
	stdout, stderr = sp.communicate()
	return stdout.splitlines()[0]

def gpu_index(pid):
	cmd="nvidia-smi | awk '$3=="+str(pid)+" {print $2}'"
	sp = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
	stdout, stderr = sp.communicate()
	return stdout.splitlines()[0]

def gpu_type(pid):
	cmd="nvidia-smi | awk '$3=="+str(pid)+" {print $4}'"
	sp = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
	stdout, stderr = sp.communicate()
	return stdout.splitlines()[0]	

def main(argv=None):
	if pid == None:
		print "No dlserver instance is monitored"
		return
	parser = argparse.ArgumentParser(description="Dlserver Performance Moitor")
	parser.add_argument("clock", type=int, help="clocktime interval / second")
	args = parser.parse_args()

	p = psutil.Process(int(pid))
	print bcolors.WARNING + "*****tx_dlserver monitor program*****" + bcolors.ENDC
	print "pid: " + str(p.pid)
	pinfo = p.as_dict(ad_value=ACCESS_DENIED)
	print "user: " + pinfo['username']
	print "started: " + datetime.datetime.fromtimestamp(
                pinfo['create_time']).strftime('%Y-%m-%d %H:%M')

	cuda_info()
	

	print bcolors.WARNING + "\n*****clock time: "+str(args.clock)+"s*****" + bcolors.ENDC
	run(args.clock)

def run(clock):
	while True:
		print ("Time: " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
		p = psutil.Process(int(pid))
		pinfo = p.as_dict(ad_value=psutil.AccessDenied)

		print bcolors.WARNING + "**Process CPU Info**" + bcolors.ENDC
		print "Memory: " + str_ntuple(pinfo['memory_full_info'], bytes2human=True)
   		print "Memory %: " + str(p.memory_percent())
   		print "cpu time: " + str_ntuple(pinfo['cpu_times'])
   		print "cpu %: " + str(p.cpu_percent(interval=1))
   		print bcolors.WARNING + "**Process GPU Info**" + bcolors.ENDC
   		print "gpu index: " + gpu_index(pid)
   		print "process type: " + gpu_type(pid)
   		print "gpu Memory: " + gpu_mem(pid)
   		print bcolors.WARNING + "**Global GPU Info**" + bcolors.ENDC
   		GPUtil.showUtilization()
   		print ""
   		time.sleep(clock)

if __name__ == "__main__":


    
    #print p.memory_percent()

    main()