/* The one layer no other language on this page can show: the sniff the
 * KERNEL does, in execve(2), when you type ./something.
 *
 * The kernel reads the first bytes of the file and offers them to each
 * registered binary-format handler in turn. Two are compiled in: ELF, which
 * wants 7f 45 4c 46, and script, which wants 23 21 - "#!". If no handler
 * claims the bytes, execve fails with ENOEXEC and the file never runs.
 *
 * We print the symbolic errno name, never strerror(): the MESSAGE text
 * differs between C libraries, and this file is an answer key.
 *
 * Build: cc -std=c11 -Wall -Wextra file_type_four_questions_c.c
 * Run:   ./a.out
 *
 * The scratch directory is built with mkdir() and getpid() rather than the
 * obvious mkdtemp(), on purpose. Under -std=c11 exactly, glibc hides mkdtemp
 * unless _POSIX_C_SOURCE is defined, and macOS hides it WHEN it is - so there
 * is no single spelling of that macro that compiles clean on both. mkdir and
 * getpid need no feature macro anywhere. See CONTRIBUTING.md, difference 23.
 */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

/* errno as a NAME. The text of strerror() is not portable; these are. */
static const char *errno_name(int e)
{
    if (e == ENOEXEC) return "ENOEXEC (exec format error)";
    if (e == ENOENT)  return "ENOENT (no such file or directory)";
    if (e == EACCES)  return "EACCES (permission denied)";
    return "some other errno";
}

/* Write bytes to a file and make it executable. */
static void put(const char *path, const char *bytes, size_t n)
{
    FILE *f = fopen(path, "wb");
    if (!f) { perror("fopen"); exit(1); }
    fwrite(bytes, 1, n, f);
    fclose(f);
    if (chmod(path, 0755) != 0) { perror("chmod"); exit(1); }
}

/* Try to execve the file. Report what the KERNEL said, not what a shell
 * would have done about it afterwards. */
static void try_exec(const char *label, const char *path)
{
    pid_t pid = fork();
    if (pid < 0) { perror("fork"); exit(1); }

    if (pid == 0) {
        char *const argv[] = { (char *)path, NULL };
        char *const envp[] = { NULL };
        execve(path, argv, envp);
        /* Only reached when execve refused. Hand errno back as the status. */
        _exit(errno);
    }

    int status = 0;
    waitpid(pid, &status, 0);
    int code = WIFEXITED(status) ? WEXITSTATUS(status) : -1;

    if (code == 0)
        printf("   %-22s ran\n", label);
    else
        printf("   %-22s refused: %s\n", label, errno_name(code));
}

int main(void)
{
    char dir[64];
    snprintf(dir, sizeof dir, "/tmp/ftype_%ld", (long)getpid());
    if (mkdir(dir, 0700) != 0) { perror("mkdir"); exit(1); }
    if (chdir(dir) != 0) { perror("chdir"); exit(1); }

    printf("1. THE KERNEL READS THE FIRST BYTES, AND ONLY THE FIRST BYTES\n");
    printf("   Four files, all with the executable bit set, all non-empty.\n");
    printf("   The only thing that differs is what is at offset zero.\n");

    /* A shebang: the 'script' handler wants exactly these two bytes. */
    const char *sh = "#!/bin/sh\nexit 0\n";
    put("has_shebang", sh, strlen(sh));

    /* Same program, no shebang. Nothing in the kernel claims it. */
    const char *bare = "exit 0\n";
    put("no_shebang", bare, strlen(bare));

    /* A shebang naming an interpreter that does not exist. */
    const char *ghost = "#!/nonexistent/interp\nexit 0\n";
    put("shebang_ghost", ghost, strlen(ghost));

    /* Bytes that look like nothing at all. */
    const char *junk = "\x01\x02\x03\x04not a format\n";
    put("junk_bytes", junk, 17);

    printf("\n");
    try_exec("#!/bin/sh", "has_shebang");
    try_exec("no shebang", "no_shebang");
    try_exec("#!/nonexistent/interp", "shebang_ghost");
    try_exec("01 02 03 04 ...", "junk_bytes");

    printf("\n");
    printf("2. READING THE TWO REFUSALS\n");
    printf("   no_shebang is a perfectly good shell script and the kernel has\n");
    printf("   no idea. It is not ELF, it does not start with #!, so no handler\n");
    printf("   claims it: ENOEXEC. When you run the same file from a shell it\n");
    printf("   works - because the SHELL catches ENOEXEC and runs the file\n");
    printf("   itself. That fallback is POSIX shell behaviour, not the kernel.\n");
    printf("\n");
    printf("   shebang_ghost is the confusing one. ENOENT means 'no such file'\n");
    printf("   and the file you named plainly exists - the missing one is the\n");
    printf("   INTERPRETER inside it, which the kernel read out of the first\n");
    printf("   line and failed to open. This is the whole story behind the\n");
    printf("   'bad interpreter: No such file or directory' that a shell shows\n");
    printf("   for a script whose shebang has a stray carriage return in it.\n");

    printf("\n");
    printf("3. WHAT THIS COSTS TO EXTEND\n");
    printf("   ELF and #! are compiled in. Every other format a Linux kernel\n");
    printf("   can launch directly - a Java class, a Mono .exe, an ARM binary\n");
    printf("   under qemu - is registered at run time through binfmt_misc, by\n");
    printf("   writing a magic string and an interpreter path into\n");
    printf("   /proc/sys/fs/binfmt_misc/register. That file is the only\n");
    printf("   extensible content-sniffing the kernel has, and it exists to\n");
    printf("   answer 'how do I run this', never 'what is this'.\n");

    const char *made[] = { "has_shebang", "no_shebang", "shebang_ghost",
                           "junk_bytes" };
    for (size_t i = 0; i < sizeof made / sizeof *made; i++) unlink(made[i]);
    if (chdir("/") == 0) rmdir(dir);
    return 0;
}
