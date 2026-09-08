// Framing a format, in Rust: the four things the type system says differently.
//
//   1. wrapping_neg IS the two's complement, and the wrap has to be asked for
//   2. the record type is an enum with an arm for what it does not know
//   3. the refusals are named, so a test cannot pass on the wrong error
//   4. parse returns Result, so an unverified record has no value to live in
//
// Layout and record-type numbers from Intel, *Hexadecimal Object File Format
// Specification*, Revision A, January 6, 1988. Compile with bare
// `rustc --edition 2024` -- no cargo, no crates.

#[derive(Debug, PartialEq, Eq, Clone, Copy)]
enum RecordType {
    Data,
    EndOfFile,
    ExtendedSegmentAddress,
    StartSegmentAddress,
    ExtendedLinearAddress,
    StartLinearAddress,
    Unknown(u8),
}

impl RecordType {
    fn from_byte(b: u8) -> RecordType {
        match b {
            0x00 => RecordType::Data,
            0x01 => RecordType::EndOfFile,
            0x02 => RecordType::ExtendedSegmentAddress,
            0x03 => RecordType::StartSegmentAddress,
            0x04 => RecordType::ExtendedLinearAddress,
            0x05 => RecordType::StartLinearAddress,
            other => RecordType::Unknown(other),
        }
    }

    fn name(self) -> &'static str {
        match self {
            RecordType::Data => "Data",
            RecordType::EndOfFile => "End of File",
            RecordType::ExtendedSegmentAddress => "Extended Segment Address",
            RecordType::StartSegmentAddress => "Start Segment Address",
            RecordType::ExtendedLinearAddress => "Extended Linear Address",
            RecordType::StartLinearAddress => "Start Linear Address",
            RecordType::Unknown(_) => "unknown to this reader",
        }
    }
}

// Every way a record can be refused, each with the number that identifies it.
// A test that expects "an error" passes when the wrong thing goes wrong.
#[derive(Debug, PartialEq, Eq)]
enum FrameError {
    NoRecordMark { at: usize },
    NotHexDigits { at: usize },
    Truncated { claims: usize, present: usize },
    BadChecksum { sum: u8 },
}

// There is no public way to build one of these without going through `parse`,
// so holding a Record is holding a record whose checksum added up to zero.
#[derive(Debug)]
struct Record {
    kind: RecordType,
    offset: u16,
    data: Vec<u8>,
}

fn checksum(body: &[u8]) -> u8 {
    body.iter().fold(0u8, |a, b| a.wrapping_add(*b)).wrapping_neg()
}

fn build(kind: u8, offset: u16, data: &[u8]) -> String {
    let mut body = vec![data.len() as u8, (offset >> 8) as u8, offset as u8, kind];
    body.extend_from_slice(data);
    let sum = checksum(&body);
    body.push(sum);
    let mut out = String::from(":");
    for b in &body {
        out.push_str(&format!("{b:02X}"));
    }
    out
}

fn byte_at(text: &str, i: usize) -> Result<u8, FrameError> {
    text.get(i..i + 2)
        .and_then(|pair| u8::from_str_radix(pair, 16).ok())
        .ok_or(FrameError::NotHexDigits { at: i })
}

fn parse_one(text: &str, at: usize) -> Result<(Record, usize), FrameError> {
    if text.as_bytes().get(at) != Some(&b':') {
        return Err(FrameError::NoRecordMark { at });
    }
    let reclen = byte_at(text, at + 1)? as usize;
    let end = at + 1 + (4 + reclen + 1) * 2;
    if end > text.len() {
        return Err(FrameError::Truncated {
            claims: reclen,
            present: (text.len() - at - 1) / 2 - 5,
        });
    }
    let mut body = Vec::new();
    let mut i = at + 1;
    while i < end {
        body.push(byte_at(text, i)?);
        i += 2;
    }
    let sum = body.iter().fold(0u8, |a, b| a.wrapping_add(*b));
    if sum != 0 {
        return Err(FrameError::BadChecksum { sum });
    }
    Ok((
        Record {
            kind: RecordType::from_byte(body[3]),
            offset: u16::from_be_bytes([body[1], body[2]]),
            data: body[4..body.len() - 1].to_vec(),
        },
        end,
    ))
}

fn hex(bytes: &[u8]) -> String {
    bytes
        .iter()
        .map(|b| format!("{b:02x}"))
        .collect::<Vec<_>>()
        .join(" ")
}

fn main() {
    let payload = "café".as_bytes(); // 63 61 66 c3 a9 -- Rust hands you UTF-8
    let record = build(0x00, 0x0100, payload);

    // ----------------------------------------------------------------------
    println!("1. THE WRAP HAS TO BE ASKED FOR");
    println!();
    let body: Vec<u8> = vec![payload.len() as u8, 0x01, 0x00, 0x00]
        .into_iter()
        .chain(payload.iter().copied())
        .collect();
    println!("   record        {record}");
    println!("   RECLEN..DATA  {}", hex(&body));
    println!();

    let mut running: u8 = 0;
    let mut wrapped_at = None;
    for (i, b) in body.iter().enumerate() {
        if running.checked_add(*b).is_none() && wrapped_at.is_none() {
            wrapped_at = Some((i, running, *b));
        }
        running = running.wrapping_add(*b);
    }
    println!("   fold with wrapping_add   {running:3}  0x{running:02X}");
    println!("   .wrapping_neg()          {:3}  0x{:02X}   <- the CHKSUM field", running.wrapping_neg(), running.wrapping_neg());
    println!();
    if let Some((i, before, b)) = wrapped_at {
        println!("   The sum passes 255 at byte {i}: {before} + {b} = {}.", before as u16 + b as u16);
        println!("   u8::checked_add returns None there, and in a debug build the plain");
        println!("   `+` would have panicked. Python spells the same step `& 0xFF` and C");
        println!("   does it silently; Rust makes you write the word `wrapping`, which is");
        println!("   the only one of the three where the modulo is visible in the source.");
    }
    println!();
    println!("   And `wrapping_neg` is not an approximation of the two's complement --");
    println!("   it IS it, which is why the checksum is one expression:");
    println!("       body.iter().fold(0u8, |a, b| a.wrapping_add(*b)).wrapping_neg()");
    println!();

    // ----------------------------------------------------------------------
    println!("2. AN ENUM WITH AN ARM FOR WHAT IT DOES NOT KNOW");
    println!();
    let future = format!(
        "{}{}{}{}",
        build(0x00, 0x0100, payload),
        build(0x06, 0x0000, &[0xDE, 0xAD, 0xBE, 0xEF]), // not one of the 1988 six
        build(0x00, 0x0200, "ż".as_bytes()),
        build(0x01, 0x0000, &[]),
    );
    println!("   {future}");
    println!();
    let mut recovered: Vec<u8> = Vec::new();
    let mut at = 0usize;
    while at < future.len() {
        let (rec, next) = parse_one(&future, at).expect("every record verifies");
        at = next;
        // The compiler requires an arm for Unknown, so a reader written today
        // cannot forget the case that arrives in five years.
        match rec.kind {
            RecordType::Data => {
                recovered.extend_from_slice(&rec.data);
                println!("   {:<24} at 0x{:04X}  {}", rec.kind.name(), rec.offset, hex(&rec.data));
            }
            RecordType::EndOfFile => println!("   {:<24} stop", rec.kind.name()),
            RecordType::Unknown(n) => println!(
                "   {:<24} type 0x{n:02X}, {} bytes skipped -- the length said how far",
                rec.kind.name(),
                rec.data.len()
            ),
            other => println!("   {:<24} not handled by this reader", other.name()),
        }
    }
    println!();
    println!("   recovered  {}  = {:?}", hex(&recovered), String::from_utf8(recovered.clone()).unwrap());
    println!();
    println!("   `Unknown(u8)` is the whole extensibility story in one arm. Without");
    println!("   it the enum would be a closed set and `from_byte` would have to");
    println!("   return an error for a record that is perfectly well formed and");
    println!("   simply newer than this program.");
    println!();

    // ----------------------------------------------------------------------
    println!("3. THE REFUSALS ARE NAMED");
    println!();
    let cases: [(&str, String); 4] = [
        ("one data character changed", {
            let mut s = record.clone();
            s.replace_range(10..11, "1");
            s
        }),
        ("checksum character changed", {
            let mut s = record.clone();
            s.replace_range(20..21, "5");
            s
        }),
        ("RECLEN claims one byte too many", {
            let mut s = record.clone();
            s.replace_range(2..3, "6");
            s
        }),
        ("a G where a hex digit goes", {
            let mut s = record.clone();
            s.replace_range(11..12, "G");
            s
        }),
    ];
    for (what, text) in &cases {
        match parse_one(text, 0) {
            Ok((rec, _)) => println!("   {what:<32} accepted: {:?}", rec.kind),
            Err(e) => println!("   {what:<32} {e:?}"),
        }
    }
    println!("   {:<32} {:?}", "no record mark at all", parse_one("05010000", 0).unwrap_err());
    println!();
    println!("   Five wrong records, four named variants -- which is what lets a test");
    println!("   assert the reason rather than just the failure. And `BadChecksum`");
    println!("   carries the sum it got, which is not decoration: a correct record");
    println!("   sums to 0, so the number it hands back is the damage itself, mod 256.");
    println!("   Row 1 changed 0x63 to 0x61, two less, and the sum came back 254 = -2.");
    println!("   Row 2 changed 0x64 to 0x65, one more, and the sum came back 1.");
    println!();

    // ----------------------------------------------------------------------
    println!("4. AN UNVERIFIED RECORD HAS NOWHERE TO LIVE");
    println!();
    let (good, _) = parse_one(&record, 0).unwrap();
    println!("   derived Debug   {good:?}");
    println!("   the same record  kind {:?}  offset 0x{:04X}  data {}", good.kind, good.offset, hex(&good.data));
    println!("   -- Rust's derived Debug prints a Vec<u8> in decimal, which is the");
    println!("   least useful base for bytes. Say `{{:02x}}` yourself for anything");
    println!("   you intend to compare against a dump.");
    println!();
    println!("   `parse_one` is the only thing that constructs a Record, and it");
    println!("   returns Err before it builds one. So there is no state in this");
    println!("   program where a Record exists and its checksum has not been");
    println!("   checked -- the question \"did anyone verify this?\" is answered by");
    println!("   the type rather than by reading the call sites. That is the same");
    println!("   move as `String` promising UTF-8, applied to a frame instead of");
    println!("   to an encoding.");
}
