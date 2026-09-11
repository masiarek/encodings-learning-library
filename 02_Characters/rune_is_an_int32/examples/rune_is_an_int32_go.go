//go:build ignore

// Go's rune is an alias for int32 -- "equivalent to int32 in all ways", in the
// words of its own documentation -- so the type that names a character checks
// nothing, and every check this page talks about is a function someone calls.
//
// The build tag keeps this file out of any package: each example in this folder
// is a program of its own, built alone.
//
// Build & run:  go run rune_is_an_int32_go.go

package main

import (
	"fmt"
	"strings"
	"unicode/utf8"
)

// Five byte strings no UTF-8 decoder may accept. Glyphs go LAST on each row:
// a two-column emoji mid-row would bend every column after it.
var cases = []struct {
	bytes string
	what  string
}{
	{"\xc3", "é cut after 1 of its 2 bytes"},
	{"\xe2\x82", "€ cut after 2 of its 3 bytes"},
	{"\xf0\x9f\x98", "😀 cut after 3 of its 4 bytes"},
	{"\xed\xa0\x80", "U+D800 in the shape of UTF-8"},
	{"\xf4\x90\x80\x80", "one past U+10FFFF, same shape"},
}

func main() {
	fmt.Println("1. A RUNE IS AN int32, AND THE TYPE CANNOT TELL THE DIFFERENCE")
	var r rune = 0xD800
	fmt.Printf("   var r rune = 0xD800        compiles, and %%T says %T\n", r)
	var n int32 = 'A'
	r = n
	fmt.Printf("   var n int32 = 'A'; r = n   compiles with no conversion; r is %d\n", r)
	fmt.Printf("   string(rune(65))           %q, not \"65\": a rune converts as a code point\n", string(rune(65)))
	fmt.Println()
	fmt.Printf("   %10s   %-15s %s\n", "value", "utf8.ValidRune", "[]byte(string(r))")
	for _, v := range []rune{-1, 0x41, 0xE9, 0xD800, 0x10FFFF, 0x110000} {
		shown := fmt.Sprintf("0x%X", v)
		if v < 0 {
			shown = fmt.Sprint(v)
		}
		fmt.Printf("   %10s   %-15t % x\n", shown, utf8.ValidRune(v), string(v))
	}
	fmt.Println("   All six compile, because each one is an int32. utf8.ValidRune is the")
	fmt.Println("   check, and it runs only where somebody writes the call. string(r) never")
	fmt.Println("   fails: for the three values it cannot encode it writes ef bf bd, which")
	fmt.Println("   is U+FFFD, and reports nothing.")
	fmt.Println()

	fmt.Println("2. THE LOOP HANDS YOU BYTE OFFSETS")
	s := "a\xc3\xa9\xe2\x82\xac\xf0\x9f\x98\x80"
	var parts []string
	for i, c := range s {
		parts = append(parts, fmt.Sprintf("%d:U+%04X", i, c))
	}
	fmt.Println(`   s = "aé€😀"`)
	fmt.Printf("   for i, r := range s        %s\n", strings.Join(parts, "  "))
	fmt.Printf("   len(s)                     %d   <- bytes\n", len(s))
	fmt.Printf("   utf8.RuneCountInString(s)  %d    <- runes\n", utf8.RuneCountInString(s))
	fmt.Println("   The index is the offset of each rune's first BYTE -- 0, 1, 3, 6 -- and")
	fmt.Println("   len() counts bytes. A Go string is a run of bytes that is usually UTF-8,")
	fmt.Println("   and nothing in the type promises that it is.")
	fmt.Println()

	fmt.Println("3. ONE U+FFFD PER BYTE -- OR PER RUN")
	fmt.Printf("   %-12s %6s %10s %12s   %s\n", "bytes", "range", "RuneCount", "ToValidUTF8", "what they are")
	replacement := string(utf8.RuneError)
	for _, c := range cases {
		ranged := 0
		for _, r := range c.bytes {
			if r == utf8.RuneError {
				ranged++
			}
		}
		runs := strings.Count(strings.ToValidUTF8(c.bytes, replacement), replacement)
		fmt.Printf("   %-12s %6d %10d %12d   %s\n", fmt.Sprintf("% x", c.bytes), ranged, utf8.RuneCountInString(c.bytes), runs, c.what)
	}
	fmt.Println("   range writes U+FFFD and moves on ONE byte, so a euro sign cut after two")
	fmt.Println("   of its bytes is two broken runes -- and utf8.RuneCountInString counts")
	fmt.Println("   them the same way. strings.ToValidUTF8 replaces each RUN of bad bytes")
	fmt.Println("   with one replacement, so the touching mistakes of rows 4 and 5 become")
	fmt.Println("   one. The Python and Rust programs on this page write one per maximal")
	fmt.Println("   subpart instead -- 1, 1, 1, 3, 4 -- and the page has the rule that")
	fmt.Println("   turns one count into the other.")
	fmt.Println()

	fmt.Println("4. A REAL U+FFFD AND A BROKEN BYTE, TOLD APART ONLY BY THE WIDTH")
	for _, c := range []struct{ bytes, what string }{
		{"\xef\xbf\xbd", "a genuine U+FFFD, correctly encoded"},
		{"\xf0\x9f\x98", "the cut-short 😀 from section 3"},
	} {
		r, size := utf8.DecodeRuneInString(c.bytes)
		fmt.Printf("   DecodeRuneInString(%s)   r == RuneError: %-5t   size %d   %s\n", fmt.Sprintf("% x", c.bytes), r == utf8.RuneError, size, c.what)
	}
	fmt.Println("   Both come back as RuneError, because a decoder that replaces has to hand")
	fmt.Println("   you SOME rune. Only the size separates them: (RuneError, 1) is the one")
	fmt.Println("   result that correct UTF-8 can never produce. A range loop hands you the")
	fmt.Println("   index and the rune but not the size, so `r == utf8.RuneError` alone")
	fmt.Println("   cannot tell a broken byte from a U+FFFD the text really contained.")
}
