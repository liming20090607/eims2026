# Read the file
with open('eims_app/templates/project_ledger/list.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JavaScript
start = content.find('<script>') + 8
end = content.rfind('</script>')
js = content[start:end]

# Check bracket balance line by line with more detail
lines = js.split('\n')
stack = []  # Track opening brackets with their positions

print("Detailed bracket tracking...\n")
for i, line in enumerate(lines, 1):
    for j, char in enumerate(line):
        if char in '{([':
            stack.append((char, i, j))
        elif char in '})]':
            if not stack:
                print(f"ERROR at line {i}, col {j}: Unexpected closing '{char}'")
                print(f"  {line.strip()}")
                continue
            
            expected_opening = {'}': '{', ')': '(', ']': '['}[char]
            actual_opening, open_line, open_col = stack[-1]
            
            if actual_opening != expected_opening:
                print(f"MISMATCH at line {i}, col {j}: Expected '{expected_opening}' but got '{actual_opening}'")
                print(f"  Opening at line {open_line}, col {open_col}")
                print(f"  Current line: {line.strip()}")
            else:
                stack.pop()

if stack:
    print(f"\nUnclosed brackets ({len(stack)} remaining):")
    for char, line, col in stack[-10:]:  # Show last 10
        print(f"  '{char}' at line {line}, col {col}")
else:
    print("\nAll brackets are properly closed!")
