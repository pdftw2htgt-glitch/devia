with open("devia.jsx", "r", encoding="utf-8") as f:
    lines = f.readlines()
cleaned = [l for l in lines if not l.strip().startswith("```")]
removed = len(lines) - len(cleaned)
with open("devia.jsx", "w", encoding="utf-8") as f:
    f.writelines(cleaned)
print(f"Termine : {removed} ligne(s) de backticks supprimee(s)")
