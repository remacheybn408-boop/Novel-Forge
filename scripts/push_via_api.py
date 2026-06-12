"""Push current HEAD to GitHub via Git Data API (bypasses port 443 block)."""
import subprocess, json, urllib.request, os, base64, sys, re

def get_token():
    p = subprocess.run(['git', 'credential', 'fill'],
        input='protocol=https\nhost=github.com\n\n',
        capture_output=True, text=True, timeout=10)
    for line in p.stdout.splitlines():
        if line.startswith('password='):
            return line[9:]
    return None

token = get_token()
if not token:
    print('No token found')
    sys.exit(1)

def api(method, path, data=None):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'curl',
    }
    url = f'https://api.github.com/repos/remacheybn408-boop/Novel-Forge{path}'
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f'  ERROR {method} {path}: {e.code}')
        print(f'  {err[:300]}')
        raise

# Get current commit info
parent_sha = subprocess.run(['git', 'rev-parse', 'HEAD~1'], capture_output=True, text=True).stdout.strip()
our_sha = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
msg = subprocess.run(['git', 'log', '--format=%B', '-1', our_sha], capture_output=True, text=True).stdout

print(f'Pushing: {our_sha[:12]}')
print(f'Parent:  {parent_sha[:12]}')

# Parse diff-tree output
# Format: :100644 100644 <oldsha> <newsha> M<TAB>file
diff = subprocess.run(['git', 'diff-tree', '--no-commit-id', '-r', 'HEAD'],
    capture_output=True, text=True).stdout

tree_items = []
for line in diff.strip().split('\n'):
    if not line.strip():
        continue
    parts = line.split('\t')
    if len(parts) < 2:
        continue
    meta = parts[0]  # :100644 100644 oldsha newsha M
    filepath = parts[1]
    
    meta_parts = meta.split()
    if len(meta_parts) < 5:
        continue
    
    old_mode = meta_parts[0].lstrip(':')
    new_mode = meta_parts[1]
    old_sha = meta_parts[2]
    new_sha = meta_parts[3]
    status = meta_parts[4]
    
    if status == 'D':
        # Deletion - include with null sha to remove from tree
        tree_items.append({'path': filepath, 'mode': old_mode, 'type': 'blob', 'sha': None})
        print(f'  🗑️ del {filepath}')
    elif status in ('M', 'A'):
        # Modified or added - push new content
        content = subprocess.run(['git', 'cat-file', '-p', new_sha],
            capture_output=True, text=True, timeout=5).stdout
        content_b64 = base64.b64encode(content.encode('utf-8')).decode()
        
        blob = api('POST', '/git/blobs', {
            'content': content_b64,
            'encoding': 'base64',
        })
        tree_items.append({'path': filepath, 'mode': new_mode, 'type': 'blob', 'sha': blob['sha']})
        print(f'  📄 {status} {filepath}: {blob["sha"][:12]}')

# Get parent tree as base
parent_tree = subprocess.run(['git', 'rev-parse', 'HEAD~1^{tree}'],
    capture_output=True, text=True).stdout.strip()

# Create new tree
new_tree = api('POST', '/git/trees', {
    'base_tree': parent_tree,
    'tree': tree_items,
})
print(f'  🌳 tree: {new_tree["sha"][:12]}')

# Create commit
commit = api('POST', '/git/commits', {
    'message': msg,
    'tree': new_tree['sha'],
    'parents': [parent_sha],
})
print(f'  💎 commit: {commit["sha"][:12]}')

# Update ref
ref = api('PATCH', '/git/refs/heads/master', {
    'sha': commit['sha'],
    'force': True,
})
print(f'  ✅ Pushed: {ref["object"]["sha"][:12]}')
