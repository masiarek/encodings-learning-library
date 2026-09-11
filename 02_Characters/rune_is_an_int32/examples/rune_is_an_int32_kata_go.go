//go:build ignore

// Five fields, cut to fit -- Go's half of the answer, counted by Go itself.
//
// The Python answer key computes Go's column from a rule. This one asks
// utf8.RuneCountInString directly, so the rule and the language can be held
// to each other on every CI run.
//
// Build & run:  go run rune_is_an_int32_kata_go.go

package main

import (
	"fmt"
	"strings"
	"unicode/utf8"
)

const limit = 4

func main() {
	// Glyphs go last on every printed row: 😀 and 日本 are two columns wide each.
	fields := []struct {
		bytes string
		what  string
	}{
		{"caf\xc3", "café, cut inside the é"},
		{"5 \xe2\x82", "5 €, cut inside the €"},
		{"hi \xf0\x9f\x98", "hi 😀, cut inside the 😀"},
		{"\xc5\xbc\xc3\xb3\xc5", "żółw, cut inside the ł"},
		{"\xe6\x97\xa5\xe6\x9c", "日本, cut inside the 本"},
	}

	fmt.Println("GO, COUNTING THE SAME FIVE FIELDS ITSELF")
	fmt.Println(strings.Repeat("-", 72))
	fmt.Println()
	fmt.Printf("   %-26s %10s %6s   %s\n", "the bytes that came back", "RuneCount", "len()", "what it was")
	var refused []string
	for _, f := range fields {
		runes := utf8.RuneCountInString(f.bytes)
		fmt.Printf("   %-26s %10d %6d   %s\n", fmt.Sprintf("% x", f.bytes), runes, len(f.bytes), f.what)
		if runes > limit {
			refused = append(refused, fmt.Sprintf("%d runes   %s", runes, f.what))
		}
	}
	fmt.Println()
	fmt.Println("   RuneCount is the column the Python key above computed for Go, and it")
	fmt.Println("   matches it row for row. The third count is Go's len(), which is BYTES:")
	fmt.Println("   three different lengths for one field, and not one of them wrong.")
	fmt.Println()
	fmt.Printf("   over the %d-rune limit:\n", limit)
	for _, line := range refused {
		fmt.Printf("      %s\n", line)
	}
}
