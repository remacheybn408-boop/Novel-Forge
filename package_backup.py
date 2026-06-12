"""打包 Novel-Forge 到 D:\引擎备份"""
import zipfile
import os
import fnmatch

root = r"D:\Novel-Forge"
out = r"D:\引擎备份\小说引擎_v0.7.5.zip"

exclude_patterns = [
    ".git/**",
    ".venv/**",
    "__pycache__/**",
    ".pytest_cache/**",
    ".uv_cache/**",
    ".story/**",
    ".agents/**",
    ".claude/**",
    "exports/**",
    "data/**",
    "database/**",
    "node_modules/**",
]

def should_exclude(relpath):
    for pat in exclude_patterns:
        if fnmatch.fnmatch(relpath, pat) or relpath.startswith(tuple(p.rstrip("/**") + "/" for p in exclude_patterns if "**" in p)):
            return True
        # Handle directory-level exclusion
        if "**" not in pat and os.path.isdir(os.path.join(root, relpath.split("/")[0])):
            if relpath.startswith(pat):
                return True
    return False

count = 0
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip excluded dirs in-place
        rel = os.path.relpath(dirpath, root)
        if rel == ".":
            rel = ""
        # Filter dirnames in-place to prevent walking into excluded dirs
        dirnames[:] = [
            d for d in dirnames
            if not should_exclude(os.path.join(rel, d) if rel else d)
        ]
        for fn in filenames:
            fpath = os.path.join(dirpath, fn)
            relpath = os.path.relpath(fpath, root)
            relpath = relpath.replace("\\", "/")
            if should_exclude(relpath):
                continue
            zf.write(fpath, relpath)
            count += 1

print(f"打包完成: {out}")
print(f"文件数: {count}")
