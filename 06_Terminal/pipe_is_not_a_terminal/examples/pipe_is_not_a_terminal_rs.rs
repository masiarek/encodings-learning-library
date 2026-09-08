// Rust asks the same question and uses the answer for nothing.
//
// std::io::stdout() is a LineWriter unconditionally — not "when it is a
// terminal" — so the ordering Python loses down a pipe survives here. This
// program proves that without needing a pty: it spawns ITSELF with both
// streams pointed at one file, then reads the file back. If stdout were block
// buffered, both OUT lines would arrive after both ERR lines, exactly as they
// do in the Python example next door.
//
// Run:  rustc --edition 2024 pipe_is_not_a_terminal_rs.rs -o p && ./p

use std::fs::File;
use std::io::{IsTerminal, Read, Write};
use std::process::{Command, Stdio};

fn child() {
    for i in 1..=2 {
        println!("OUT {i}");
        eprintln!("ERR {i}");
    }
}

fn main() {
    if std::env::args().nth(1).as_deref() == Some("child") {
        return child();
    }

    println!("1. RUST ASKS THE SAME QUESTION");
    println!("   stdout.is_terminal() = {}", std::io::stdout().is_terminal());
    println!("   stderr.is_terminal() = {}", std::io::stderr().is_terminal());
    println!("   stdin.is_terminal()  = {}", std::io::stdin().is_terminal());
    println!("   std::io::IsTerminal, stable since 1.70. Same syscall as the");
    println!("   shell's [ -t 1 ] and Python's sys.stdout.isatty(), and false");
    println!("   here for the same reason: a test runner captured the output.");

    println!();
    println!("2. AND CHANGES NOTHING ABOUT HOW IT WRITES");
    let dir = std::env::temp_dir().join(format!("rs_pipe_demo_{}", std::process::id()));
    std::fs::create_dir_all(&dir).expect("mkdir");
    let path = dir.join("merged.txt");
    let sink = File::create(&path).expect("create");
    let me = std::env::current_exe().expect("current_exe");
    Command::new(me)
        .arg("child")
        .stdout(Stdio::from(sink.try_clone().expect("clone")))
        .stderr(Stdio::from(sink))
        .status()
        .expect("spawn");
    let mut merged = String::new();
    File::open(&path).expect("open").read_to_string(&mut merged).expect("read");
    std::fs::remove_dir_all(&dir).ok();

    println!("   The child wrote OUT 1, ERR 1, OUT 2, ERR 2 with both streams");
    println!("   redirected to one plain FILE — no terminal anywhere. It came");
    println!("   back in this order:");
    println!("     {}", merged.lines().collect::<Vec<_>>().join(" "));
    println!("   In order. Python, given exactly this arrangement, returns");
    println!("   ERR 1 ERR 2 OUT 1 OUT 2, because its stdout switched to block");
    println!("   buffering the moment it stopped being a terminal. Rust's did");
    println!("   not switch, because it never asked.");

    println!();
    println!("3. THE TRADE, WHICH IS A REAL ONE");
    println!("   A LineWriter flushes on every newline, so a program printing a");
    println!("   million lines pays a write syscall per line. Rust's answer is");
    println!("   to make the fast path something you ASK for rather than");
    println!("   something the environment picks for you:");
    let mut out = std::io::BufWriter::new(std::io::stdout().lock());
    writeln!(out, "     BufWriter::new(stdout().lock())  <- this line came").expect("write");
    writeln!(out, "     through one, and is block buffered until the flush").expect("write");
    out.flush().expect("flush");
    println!("   That is the same buffering Python gives you by default down a");
    println!("   pipe — with two differences that matter: you wrote it down, so");
    println!("   the next reader can see it; and the compiler will not let you");
    println!("   forget that it can fail, because flush() returns a Result.");
    println!("   The bug on the Python page — output lost when a process exits");
    println!("   without flushing — is still reachable here. It is just no");
    println!("   longer the default, and no longer invisible.");
}
