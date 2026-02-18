//go:build linux && amd64

package python_syscall

import "syscall"

const (
	SYS_GETRANDOM = 318
	SYS_RSEQ      = 334
	SYS_SENDMMSG  = 307
	SYS_CLONE3    = 435
)

var ALLOW_SYSCALLS = []int{
	// file io
	syscall.SYS_NEWFSTATAT, syscall.SYS_IOCTL, syscall.SYS_LSEEK, syscall.SYS_GETDENTS64,
	syscall.SYS_WRITE, syscall.SYS_CLOSE, syscall.SYS_OPENAT, syscall.SYS_READ,
	syscall.SYS_FSTAT, syscall.SYS_PREAD64, syscall.SYS_DUP, syscall.SYS_FCNTL,
	syscall.SYS_ACCESS, syscall.SYS_READLINK, syscall.SYS_GETCWD,
	// thread
	syscall.SYS_FUTEX,
	// memory
	syscall.SYS_MMAP, syscall.SYS_BRK, syscall.SYS_MPROTECT, syscall.SYS_MUNMAP, syscall.SYS_RT_SIGRETURN,
	syscall.SYS_MREMAP, syscall.SYS_MBIND, syscall.SYS_MADVISE,

	// user/group
	syscall.SYS_SETUID, syscall.SYS_SETGID, syscall.SYS_GETUID, syscall.SYS_GETGID,
	syscall.SYS_GETEUID, syscall.SYS_GETEGID,
	// process
	syscall.SYS_GETPID, syscall.SYS_GETPPID, syscall.SYS_GETTID,
	syscall.SYS_EXIT, syscall.SYS_EXIT_GROUP,
	syscall.SYS_TGKILL, syscall.SYS_RT_SIGACTION, syscall.SYS_IOCTL,
	syscall.SYS_CLONE, SYS_CLONE3,
	syscall.SYS_SCHED_YIELD, syscall.SYS_SCHED_GETAFFINITY,
	syscall.SYS_SET_ROBUST_LIST, syscall.SYS_GET_ROBUST_LIST, syscall.SYS_SET_TID_ADDRESS,
	syscall.SYS_ARCH_PRCTL, syscall.SYS_PRLIMIT64, syscall.SYS_SYSINFO, SYS_RSEQ,
	syscall.SYS_SOCKETPAIR, syscall.SYS_GETSOCKNAME,

	// time
	syscall.SYS_CLOCK_GETTIME, syscall.SYS_GETTIMEOFDAY, syscall.SYS_NANOSLEEP,
	syscall.SYS_EPOLL_CREATE1,
	syscall.SYS_EPOLL_CTL, syscall.SYS_EPOLL_PWAIT, syscall.SYS_EPOLL_WAIT, syscall.SYS_CLOCK_NANOSLEEP, syscall.SYS_PSELECT6,
	syscall.SYS_TIME,

	syscall.SYS_RT_SIGPROCMASK, syscall.SYS_SIGALTSTACK, syscall.SYS_UNAME, SYS_GETRANDOM,
}

var ALLOW_ERROR_SYSCALLS = []int{
	syscall.SYS_MKDIRAT,
	syscall.SYS_MKDIR,
}

var ALLOW_NETWORK_SYSCALLS = []int{
	syscall.SYS_SOCKET, syscall.SYS_CONNECT, syscall.SYS_BIND, syscall.SYS_LISTEN, syscall.SYS_ACCEPT, syscall.SYS_SENDTO, syscall.SYS_RECVFROM,
	syscall.SYS_GETSOCKNAME, syscall.SYS_RECVMSG, syscall.SYS_GETPEERNAME, syscall.SYS_SETSOCKOPT, syscall.SYS_PPOLL, syscall.SYS_UNAME,
	syscall.SYS_SENDMSG, SYS_SENDMMSG, syscall.SYS_GETSOCKOPT,
	syscall.SYS_FSTAT, syscall.SYS_FCNTL, syscall.SYS_FSTATFS, syscall.SYS_POLL, syscall.SYS_EPOLL_PWAIT,
}
