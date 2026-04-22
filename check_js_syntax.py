import re

# Read the file
with open('eims_app/templates/project_ledger/list.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JavaScript
start = content.find('<script>') + 8
end = content.rfind('</script>')
js = content[start:end]

# Check bracket balance line by line
lines = js.split('\n')
brace_count = 0
paren_count = 0
bracket_count = 0

print("Checking bracket balance...\n")
for i, line in enumerate(lines, 1):
    for char in line:
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        elif char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        elif char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
    
    # Show lines with imbalances
    if brace_count < 0 or paren_count < 0 or bracket_count < 0:
        print(f"Line {i}: {{={brace_count}, (={paren_count}, [={bracket_count}")
        print(f"  {line.strip()}")

print(f"\nFinal counts:")
print(f"  Braces {{}}: {brace_count}")
print(f"  Parentheses (): {paren_count}")
print(f"  Brackets []: {bracket_count}")
print(f"  Total JS lines: {len(lines)}")
