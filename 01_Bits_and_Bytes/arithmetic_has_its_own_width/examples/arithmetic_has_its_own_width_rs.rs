// A byte is eight bits wide, and in Rust so is the arithmetic over it. The
// widening C performs for you is a cast you have to write.
//
// Build & run:  rustc --edition 2024 arithmetic_has_its_own_width_rs.rs && ./arithmetic_has_its_own_width_rs

fn main() {
    let c: u8 = 255;
    let s: i8 = -5;

    println!("1. THE WIDTH IS IN THE TYPE, AND THE OPERATOR STAYS INSIDE IT");
    println!("   c                       = {c:<6} 1111 1111");
    println!("   c << 2                  = {:<6} still a u8, so the two high bits are gone", c << 2);
    println!("   size_of_val(&(c << 2))  = {:<6} the expression did not become anything wider",
             size_of_val(&(c << 2)));
    println!("   There is no promotion here. `c << 2` is a u8 because `c` is a u8, and the");
    println!("   answer 252 is the whole answer -- nothing was computed and then thrown away.");
    println!();

    println!("2. WIDENING IS A CAST YOU HAVE TO WRITE DOWN");
    println!("   (c as u32) << 2         = {:<6} the number C would have computed for you", (c as u32) << 2);
    println!("   Same bits, same operator, different answer -- and the difference is one");
    println!("   visible `as u32`. That is the whole trade: Rust makes you say which");
    println!("   arithmetic you meant, and in exchange the expression cannot surprise you.");
    println!();

    println!("3. THE TYPE PICKS THE SHIFT. THE BITS DO NOT.");
    let u: u8 = 0b1111_1011;
    println!("   s: i8  = {:<5} bits {:08b}", s, s as u8);
    println!("   u: u8  = {:<5} bits {:08b}   <- the same eight bits", u, u);
    println!("   s >> 3 = {:<5} arithmetic: the sign bit is copied in on the left", s >> 3);
    println!("   u >> 3 = {:<5} logical:    zeros are shifted in on the left", u >> 3);
    println!("   One byte, one operator, two answers. Nothing in `>>` chose between them;");
    println!("   the declaration did, several lines earlier.");
    println!();

    println!("4. DIVISION FOLLOWS C, AND PYTHON'S ANSWER HAS ITS OWN NAME");
    println!("   -5 / 8                  = {:<6} rounds toward zero, exactly as C does", -5i32 / 8);
    println!("   -5 % 8                  = {:<6} so the remainder is negative", -5i32 % 8);
    println!("   (-5).div_euclid(8)      = {:<6} rounds down, exactly as Python's // does", (-5i32).div_euclid(8));
    println!("   (-5).rem_euclid(8)      = {:<6} so this remainder never is", (-5i32).rem_euclid(8));
    let shift_vs_div = (-8i32..0).filter(|x| (x >> 3) != (x / 8)).count();
    let shift_vs_euclid = (-8i32..0).filter(|x| (x >> 3) != x.div_euclid(8)).count();
    println!("   Counted over -8..-1: `>>` differs from `/` on {shift_vs_div} values and from");
    println!("   `div_euclid` on {shift_vs_euclid}. Four spellings of division, and you pick one by name.");
    println!();

    println!("5. WHAT RUST CHECKS, AND THE ONE THING IT DOES NOT");
    println!("   250u8.checked_add(10)   = {:?}   overflow of + is caught", 250u8.checked_add(10));
    println!("   255u8.checked_shl(2)    = {:?} but checked_shl only checks the AMOUNT,", 255u8.checked_shl(2));
    println!("   255u8.checked_shl(8)    = {:?}   and 8 is not a legal shift for a u8", 255u8.checked_shl(8));
    println!("   So a left shift drops bits off the top in silence while an addition that");
    println!("   overflows by one bit is refused. The rule is narrower than `Rust checks");
    println!("   arithmetic`: a shift is checked for asking too much, not for losing data.");
}
