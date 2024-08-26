import os
import ctypes
from ctypes import wintypes

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
LOCKFILE_FAIL_IMMEDIATELY = 0x00000001
LOCKFILE_EXCLUSIVE_LOCK = 0x00000002
FILE_BEGIN = 0
F_GETFL = 3  # Get file descriptor flags
F_SETFL = 4  # Set file descriptor flags
FILE_ATTRIBUTE_READONLY = 0x00000001
FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_FLAG_OVERLAPPED = 0x40000000

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

GetFileAttributesW = kernel32.GetFileAttributesW
GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
GetFileAttributesW.restype = wintypes.DWORD

SetFileAttributesW = kernel32.SetFileAttributesW
SetFileAttributesW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD]
SetFileAttributesW.restype = wintypes.BOOL

CreateFileW = kernel32.CreateFileW
CreateFileW.argtypes = [
    wintypes.LPCWSTR,  # lpFileName
    wintypes.DWORD,    # dwDesiredAccess
    wintypes.DWORD,    # dwShareMode
    wintypes.LPVOID,   # lpSecurityAttributes
    wintypes.DWORD,    # dwCreationDisposition
    wintypes.DWORD,    # dwFlagsAndAttributes
    wintypes.HANDLE    # hTemplateFile
]
CreateFileW.restype = wintypes.HANDLE

LockFileEx = kernel32.LockFileEx
LockFileEx.argtypes = [
    wintypes.HANDLE,   # hFile
    wintypes.DWORD,    # dwFlags
    wintypes.DWORD,    # dwReserved
    wintypes.DWORD,    # nNumberOfBytesToLockLow
    wintypes.DWORD,    # nNumberOfBytesToLockHigh
    wintypes.LPVOID    # lpOverlapped
]
LockFileEx.restype = wintypes.BOOL

UnlockFileEx = kernel32.UnlockFileEx
UnlockFileEx.argtypes = [
    wintypes.HANDLE,   # hFile
    wintypes.DWORD,    # dwReserved
    wintypes.DWORD,    # nNumberOfBytesToUnlockLow
    wintypes.DWORD,    # nNumberOfBytesToUnlockHigh
    wintypes.LPVOID    # lpOverlapped
]
UnlockFileEx.restype = wintypes.BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL

DeviceIoControl = kernel32.DeviceIoControl
DeviceIoControl.argtypes = [
    wintypes.HANDLE,   # hDevice
    wintypes.DWORD,    # dwIoControlCode
    wintypes.LPVOID,   # lpInBuffer
    wintypes.DWORD,    # nInBufferSize
    wintypes.LPVOID,   # lpOutBuffer
    wintypes.DWORD,    # nOutBufferSize
    wintypes.LPDWORD,  # lpBytesReturned
    wintypes.LPVOID    # lpOverlapped
]
DeviceIoControl.restype = wintypes.BOOL

def check_bool(result, func, args):
    if not result:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

LockFileEx.errcheck = check_bool
UnlockFileEx.errcheck = check_bool

LOCK_SH = 0x01  
LOCK_EX = 0x02  
LOCK_UN = 0x08  
LOCK_NB = 0x04  

class Fcntl:
    def __init__(self, filepath):
        self.handle = CreateFileW(
            filepath, GENERIC_READ | GENERIC_WRITE,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None, OPEN_EXISTING, 0, None
        )
        if self.handle == wintypes.INVALID_HANDLE_VALUE:
            raise ctypes.WinError(ctypes.get_last_error())

    def fcntl(fd, cmd, arg=0):
        """Implements fcntl functionality for file control on Windows."""
        # Convert file descriptor to file path
        file_path = os.path.abspath(fd_to_path(fd))
        
        if cmd == F_GETFL:
            # Get file attributes using Windows API
            attrs = GetFileAttributesW(file_path)
            if attrs == 0xFFFFFFFF:
                raise ctypes.WinError(ctypes.get_last_error())

            # Translate the attributes to flags
            if attrs & FILE_ATTRIBUTE_READONLY:
                return os.O_RDONLY
            else:
                return os.O_RDWR

        elif cmd == F_SETFL:
            # Set file attributes using Windows API
            if arg & os.O_RDONLY:
                success = SetFileAttributesW(file_path, FILE_ATTRIBUTE_READONLY)
            elif arg & os.O_RDWR:
                success = SetFileAttributesW(file_path, FILE_ATTRIBUTE_NORMAL)
            else:
                raise ValueError("Unsupported flag for F_SETFL.")
            
            if not success:
                raise ctypes.WinError(ctypes.get_last_error())

            return 0

        else:
            raise ValueError(f"Command {cmd} not supported.")

def fd_to_path(fd):
    """Convert file descriptor to file path."""
    try:
        return os.readlink(f'/proc/self/fd/{fd}')
    except OSError:
        raise ValueError("Cannot resolve file descriptor to path.")

    def flock(self, fd, operation):
        """Mimics flock for file locking."""
        if operation & LOCK_UN:
            UnlockFileEx(self.handle, 0, 0xFFFFFFFF, 0xFFFFFFFF, None)
        else:
            flags = 0
            if operation & LOCK_EX:
                flags |= LOCKFILE_EXCLUSIVE_LOCK
            if operation & LOCK_NB:
                flags |= LOCKFILE_FAIL_IMMEDIATELY
            LockFileEx(self.handle, flags, 0, 0xFFFFFFFF, 0xFFFFFFFF, None)

    def ioctl(self, fd, request, arg=0):
        """Mimics ioctl functionality for device-specific operations."""

        out_buffer = ctypes.create_string_buffer(1024)
        bytes_returned = wintypes.DWORD(0)
        success = DeviceIoControl(
            self.handle,
            request,
            ctypes.byref(ctypes.c_int(arg)),
            ctypes.sizeof(ctypes.c_int),
            out_buffer,
            ctypes.sizeof(out_buffer),
            ctypes.byref(bytes_returned),
            None
        )
        if not success:
            raise ctypes.WinError(ctypes.get_last_error())
        return out_buffer.raw[:bytes_returned.value]

    def close(self):
        """Closes the file handle."""
        if self.handle:
            CloseHandle(self.handle)
            self.handle = None

