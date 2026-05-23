#!/usr/bin/env python3
"""
init_db.py — 数据库初始化脚本

用法:
  python scripts/init_db.py --config config.json
  python scripts/init_db.py --db-path ./data/novel_memory.db
"""

import sqlite3, sys, argparse, json, os
from pathlib import Path


def load_config(config_path=None):
    cfg = {
        "db_path": "./data/novel_memory.db",
    }
    if config_path and Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            user_cfg = json.load(f)
        cfg.update(user_cfg)
    return cfg


def find_schema(script_dir):
    """Find schema.sql relative to the project root"""
    # Try relative to script directory
    candidates = [
        script_dir.parent / "database" / "schema.sql",
        script_dir.parent.parent / "database" / "schema.sql",
        Path("database/schema.sql"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def init_db(db_path, schema_path):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Use executescript for full SQL file (handles multi-line statements)
        conn.executescript(schema_sql)
        conn.commit()

        # Verify: list all tables (excluding FTS internal tables)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts_%' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_fts' ORDER BY name")
        fts_tables = [r[0] for r in cur.fetchall()]
        conn.close()

        print(f"\n[OK] 数据库初始化完成: {db_path}")
        print(f"  普通表 ({len(tables)}): {', '.join(tables)}")
        if fts_tables:
            print(f"  FTS5索引 ({len(fts_tables)}): {', '.join(fts_tables)}")
        return True

    except Exception as e:
        conn.close()
        print(f"[FAIL] 数据库初始化失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Novel Pipeline — 数据库初始化")
    parser.add_argument("--config", default=None, help="配置文件路径 (默认: config.json)")
    parser.add_argument("--db-path", default=None, help="数据库路径 (覆盖配置文件)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.db_path:
        cfg["db_path"] = args.db_path

    db_path = cfg["db_path"]
    script_dir = Path(__file__).resolve().parent
    schema_path = find_schema(script_dir)

    if not schema_path:
        print(f"[FAIL] 找不到 database/schema.sql")
        print(f"  当前脚本目录: {script_dir}")
        sys.exit(1)

    print(f"数据库: {db_path}")
    print(f"Schema: {schema_path}")
    print(f"初始化中...")

    success = init_db(db_path, schema_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
