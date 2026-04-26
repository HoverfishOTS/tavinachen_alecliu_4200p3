import sys

def solve():
    valid_pairs = []
    cells = [(r, c) for r in range(8) for c in range(8)]
    
    for r1, c1 in cells:
        for r2, c2 in cells:
            if (r1, c1) < (r2, c2):
                if r1 == r2 and abs(c1 - c2) <= 3:
                    valid_pairs.append(((r1, c1), (r2, c2)))
                elif c1 == c2 and abs(r1 - r2) <= 3:
                    valid_pairs.append(((r1, c1), (r2, c2)))
                    
    print(f"Total valid pairs: {len(valid_pairs)}")
    
    lines = []
    for r in range(8):
        for c in range(5):
            lines.append([(r, c+i) for i in range(4)])
    for c in range(8):
        for r in range(5):
            lines.append([(r+i, c) for i in range(4)])
            
    print(f"Total lines: {len(lines)}")
    
    from z3 import Bool, Solver, Or, Sum, If, sat
    
    pair_vars = [Bool(f"p_{i}") for i in range(len(valid_pairs))]
    
    s = Solver()
    
    # 1. Every cell is in AT MOST one selected pair
    for cell in cells:
        cell_pairs = [pair_vars[i] for i, p in enumerate(valid_pairs) if cell in p]
        s.add(Sum([If(v, 1, 0) for v in cell_pairs]) <= 1)
        
    # 2. Every line contains at least one selected pair
    for line in lines:
        line_pairs = []
        for i, p in enumerate(valid_pairs):
            if p[0] in line and p[1] in line:
                line_pairs.append(pair_vars[i])
        s.add(Or(line_pairs))
        
    print("Solving...")
    res = s.check()
    if res == sat:
        print("Found a pairing!")
        m = s.model()
        selected = [valid_pairs[i] for i in range(len(valid_pairs)) if m.evaluate(pair_vars[i])]
        for p in selected:
            print(p)
    else:
        print("No pairing exists!")

if __name__ == "__main__":
    solve()
