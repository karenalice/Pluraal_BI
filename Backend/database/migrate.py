import json
import psycopg
from psycopg.rows import dict_row
import pymysql

# 1. Read original data
orig_conn = psycopg.connect(
    host="aws-0-us-east-1.pooler.supabase.com",
    port=6543,
    dbname="postgres",
    user="postgres.xwqllkbwtverxtxmqolb",
    password="0Utl@nd&r2001",
    row_factory=dict_row
)
orig_cur = orig_conn.cursor()

orig_cur.execute("""
    SELECT id_usuario, nome_completo_usuario, email, senha, hierarquia,
           ativo, trocar_senha_no_primeiro_acesso, pode_criar_usuario,
           criado_por_usuario_id, criado_em, token_versao, foto_perfil,
           paginas_permitidas, pode_simular_visao, limite_criacao_usuarios,
           pode_cadastrar_escola, data_expiracao_login
    FROM pluraal.usuario ORDER BY id_usuario
""")
users = orig_cur.fetchall()
print(f"Loaded {len(users)} users from original DB.")

orig_cur.execute("""
    SELECT id_acesso, id_usuario, tipo, sigla_uniao, sigla_associacao, id_escolas
    FROM pluraal.usuario_acesso ORDER BY id_acesso
""")
acessos = orig_cur.fetchall()
print(f"Loaded {len(acessos)} acessos from original DB.")

orig_cur.execute("""
    SELECT id_escolas, "ESCOLA", "UNIAO", "SIGLA_UNIAO", "ASSOCIACAO", "SIGLA_ASSOCIACAO"
    FROM pluraal.escolas_pluraal ORDER BY id_escolas
""")
escolas = orig_cur.fetchall()
print(f"Loaded {len(escolas)} escolas from original DB.")
orig_conn.close()

# Initial Power BI links from link power bi.txt
dashboards_initial = [
    {"nome": "ASUMA", "link": "https://app.powerbi.com/view?r=eyJrIjoiN2EzNzI4ZjMtNDRmYS00MWRlLWFmNmEtYWU4OTE3MGFkNmY2IiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "AMA", "link": "https://app.powerbi.com/view?r=eyJrIjoiNjdmZjU1NWMtMTliYi00NmM3LTkyMGYtMzgzYjU4YzhhN2FhIiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "ANPA", "link": "https://app.powerbi.com/view?r=eyJrIjoiYWZlODk2OTYtNjZkNi00ZmIxLWEwMDQtZDg0Y2VhZTAzNTg0IiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "BLUMENAU", "link": "https://app.powerbi.com/view?r=eyJrIjoiZTZkNWUyMWQtY2FmMS00ZGEzLWJmYWUtMjE4NGNiOTFmZTAyIiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "IABC", "link": "https://app.powerbi.com/view?r=eyJrIjoiYmE0MjI4NmYtNTcwYS00Zjg1LWE1NjQtODUwM2EwODg0YTY1IiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "MNEM", "link": "https://app.powerbi.com/view?r=eyJrIjoiOTA4MDJmZjAtOTlhMC00YWRlLTk3OWItZTgyMTMyNTQxNDk4IiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "MTO", "link": "https://app.powerbi.com/view?r=eyJrIjoiNTZiNDdhOTAtNTgwMy00Y2RmLWIyNjQtZGYyYzg3YmY3ZjEyIiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "AP", "link": "https://app.powerbi.com/view?r=eyJrIjoiNTU1YWQ3MjYtOTU3Zi00YjdjLTkyOWMtNzYwZTZhY2NkMmQzIiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "APSE", "link": "https://app.powerbi.com/view?r=eyJrIjoiZjcyOTYwNjAtYmU5NS00NzE5LThlNGQtZDRmZjVmNzEwODE3IiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "ALM", "link": "https://app.powerbi.com/view?r=eyJrIjoiNDVjNTgzNTYtZjhmOC00NGIwLTg1ZTAtYjczYjI3NjU4MWEyIiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "UNASP", "link": "https://app.powerbi.com/view?r=eyJrIjoiZjZkZjlmZjctZTM1Yi00NjlhLTlkNjEtNGQ2ZmNmY2E3NDk2IiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "UNEB", "link": "https://app.powerbi.com/view?r=eyJrIjoiNjdhNzUxZjctMTFlNi00YjkyLTk3NTQtZWIxMjI4Nzk1N2Y0IiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "UNOB", "link": "https://app.powerbi.com/view?r=eyJrIjoiMmIzMWQxNjUtODcxYy00OTA5LWJhMjgtN2I1YTEyYjZlNjdlIiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "ACP", "link": "https://app.powerbi.com/view?r=eyJrIjoiYTdkYTY3ZGMtZDkwOC00NTFkLTljOGMtNjNmNDUxMWFjMDJjIiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "ACSR", "link": "https://app.powerbi.com/view?r=eyJrIjoiZDUzZDNjMzAtNTgxYS00OTEwLWI0MDMtYjk1Y2M0ODAwNGU5IiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "IAP", "link": "https://app.powerbi.com/view?r=eyJrIjoiYmJhZDdkODMtNzliNi00NDgxLTk1MDQtOGNlZmVjZWY0NWJhIiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"},
    {"nome": "Paulína", "link": "https://app.powerbi.com/view?r=eyJrIjoiZTQwMmYxYjYtNzI5NC00YzFkLWE0OTUtZmUyYWNiY2JlOTFlIiwidCI6ImM4NGI3YzEwLTdlZWYtNDFlNS1hYjllLTRlMWQ1NjlkNzIyYiJ9"}
]

# 2. Populate Supabase (PostgreSQL)
print("\n--- Migrating to Supabase (PostgreSQL) ---")
suba_conn = psycopg.connect(
    host="aws-0-us-east-2.pooler.supabase.com",
    port=6543,
    dbname="postgres",
    user="postgres.nplfvbrquxcfpvrlgurw",
    password="0Utl@nd&r2001",
    row_factory=dict_row
)
suba_cur = suba_conn.cursor()

# Create schema
suba_cur.execute("CREATE SCHEMA IF NOT EXISTS bi_pluraal;")

# Create tables
suba_cur.execute("""
CREATE TABLE IF NOT EXISTS bi_pluraal.usuario (
    id_usuario BIGSERIAL PRIMARY KEY,
    nome_completo_usuario TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    hierarquia TEXT NOT NULL DEFAULT 'escola',
    ativo BOOLEAN NOT NULL DEFAULT true,
    trocar_senha_no_primeiro_acesso BOOLEAN NOT NULL DEFAULT true,
    pode_criar_usuario BOOLEAN NOT NULL DEFAULT false,
    pode_criar_link BOOLEAN NOT NULL DEFAULT false,
    pode_simular_visao BOOLEAN DEFAULT false,
    limite_criacao_usuarios INTEGER,
    criado_por_usuario_id BIGINT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    token_versao INTEGER NOT NULL DEFAULT 1,
    foto_perfil TEXT,
    paginas_permitidas TEXT[] DEFAULT ARRAY['bi'],
    pode_cadastrar_escola BOOLEAN DEFAULT false,
    data_expiracao_login DATE
);
""")

suba_cur.execute("""
CREATE TABLE IF NOT EXISTS bi_pluraal.escolas_pluraal (
    id_escolas INTEGER PRIMARY KEY,
    "ESCOLA" TEXT,
    "UNIAO" TEXT,
    "SIGLA_UNIAO" TEXT,
    "ASSOCIACAO" TEXT,
    "SIGLA_ASSOCIACAO" TEXT
);
""")

suba_cur.execute("""
CREATE TABLE IF NOT EXISTS bi_pluraal.usuario_acesso (
    id_acesso BIGSERIAL PRIMARY KEY,
    id_usuario BIGINT NOT NULL REFERENCES bi_pluraal.usuario(id_usuario) ON DELETE CASCADE,
    tipo TEXT NOT NULL,
    sigla_uniao TEXT,
    sigla_associacao TEXT,
    id_escolas INTEGER REFERENCES bi_pluraal.escolas_pluraal(id_escolas) ON DELETE CASCADE
);
""")

suba_cur.execute("""
CREATE TABLE IF NOT EXISTS bi_pluraal.powerbi_link (
    id_link BIGSERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    link TEXT NOT NULL,
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT true,
    criado_por_usuario_id BIGINT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
""")

suba_cur.execute("""
CREATE TABLE IF NOT EXISTS bi_pluraal.usuario_powerbi (
    id BIGSERIAL PRIMARY KEY,
    id_usuario BIGINT NOT NULL REFERENCES bi_pluraal.usuario(id_usuario) ON DELETE CASCADE,
    id_link BIGINT NOT NULL REFERENCES bi_pluraal.powerbi_link(id_link) ON DELETE CASCADE,
    atribuido_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atribuido_por_usuario_id BIGINT,
    UNIQUE(id_usuario, id_link)
);
""")

# Insert escolas
for e in escolas:
    suba_cur.execute("""
        INSERT INTO bi_pluraal.escolas_pluraal (id_escolas, "ESCOLA", "UNIAO", "SIGLA_UNIAO", "ASSOCIACAO", "SIGLA_ASSOCIACAO")
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_escolas) DO UPDATE
        SET "ESCOLA"=EXCLUDED."ESCOLA", "UNIAO"=EXCLUDED."UNIAO", "SIGLA_UNIAO"=EXCLUDED."SIGLA_UNIAO",
            "ASSOCIACAO"=EXCLUDED."ASSOCIACAO", "SIGLA_ASSOCIACAO"=EXCLUDED."SIGLA_ASSOCIACAO";
    """, (e["id_escolas"], e["ESCOLA"], e["UNIAO"], e["SIGLA_UNIAO"], e["ASSOCIACAO"], e["SIGLA_ASSOCIACAO"]))

# Insert users
for u in users:
    is_master = (u["hierarquia"] == "Master")
    suba_cur.execute("""
        INSERT INTO bi_pluraal.usuario (
            id_usuario, nome_completo_usuario, email, senha, hierarquia,
            ativo, trocar_senha_no_primeiro_acesso, pode_criar_usuario, pode_criar_link,
            pode_simular_visao, limite_criacao_usuarios, criado_por_usuario_id,
            criado_em, token_versao, foto_perfil, paginas_permitidas,
            pode_cadastrar_escola, data_expiracao_login
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s
        ) ON CONFLICT (id_usuario) DO UPDATE
        SET nome_completo_usuario=EXCLUDED.nome_completo_usuario,
            email=EXCLUDED.email,
            senha=EXCLUDED.senha,
            hierarquia=EXCLUDED.hierarquia,
            pode_criar_link=EXCLUDED.pode_criar_link;
    """, (
        u["id_usuario"], u["nome_completo_usuario"], u["email"], u["senha"], u["hierarquia"],
        u["ativo"], u["trocar_senha_no_primeiro_acesso"], u["pode_criar_usuario"], is_master,
        u["pode_simular_visao"], u["limite_criacao_usuarios"], u["criado_por_usuario_id"],
        u["criado_em"], u["token_versao"], u["foto_perfil"], ["bi"],
        u["pode_cadastrar_escola"], u["data_expiracao_login"]
    ))

suba_cur.execute("SELECT setval('bi_pluraal.usuario_id_usuario_seq', (SELECT COALESCE(MAX(id_usuario), 1) FROM bi_pluraal.usuario));")

# Insert initial powerbi links
link_ids = []
for dash in dashboards_initial:
    suba_cur.execute("""
        SELECT id_link FROM bi_pluraal.powerbi_link WHERE nome = %s;
    """, (dash["nome"],))
    found = suba_cur.fetchone()
    if found:
        link_id = found["id_link"]
    else:
        suba_cur.execute("""
            INSERT INTO bi_pluraal.powerbi_link (nome, link, descricao, ativo, criado_por_usuario_id)
            VALUES (%s, %s, %s, true, 1)
            RETURNING id_link;
        """, (dash["nome"], dash["link"], f"Dashboard Power BI {dash['nome']}"))
        link_id = suba_cur.fetchone()["id_link"]
    link_ids.append(link_id)

# Assign all dashboards to Master users (1 and 63), and assign ASUMA & AMA to karen david (78)
for u in users:
    uid = u["id_usuario"]
    if u["hierarquia"] == "Master":
        for lid in link_ids:
            suba_cur.execute("""
                INSERT INTO bi_pluraal.usuario_powerbi (id_usuario, id_link, atribuido_por_usuario_id)
                VALUES (%s, %s, 1)
                ON CONFLICT (id_usuario, id_link) DO NOTHING;
            """, (uid, lid))
    elif uid == 78:
        # Give 2 links to karen david for testing multi-bi home
        for lid in link_ids[:2]:
            suba_cur.execute("""
                INSERT INTO bi_pluraal.usuario_powerbi (id_usuario, id_link, atribuido_por_usuario_id)
                VALUES (%s, %s, 1)
                ON CONFLICT (id_usuario, id_link) DO NOTHING;
            """, (uid, lid))

suba_conn.commit()
suba_conn.close()
print("Supabase migration completed successfully!")

# 3. Populate MySQL
print("\n--- Migrating to MySQL ---")
mysql_conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="Mudar@123",
    database="bi_pluraal",
    charset="utf8mb4"
)
my_cur = mysql_conn.cursor()

my_cur.execute("""
CREATE TABLE IF NOT EXISTS escolas_pluraal (
    id_escolas INT PRIMARY KEY,
    ESCOLA VARCHAR(255),
    UNIAO VARCHAR(255),
    SIGLA_UNIAO VARCHAR(50),
    ASSOCIACAO VARCHAR(255),
    SIGLA_ASSOCIACAO VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

my_cur.execute("""
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario BIGINT AUTO_INCREMENT PRIMARY KEY,
    nome_completo_usuario VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    hierarquia VARCHAR(50) NOT NULL DEFAULT 'escola',
    ativo BOOLEAN NOT NULL DEFAULT true,
    trocar_senha_no_primeiro_acesso BOOLEAN NOT NULL DEFAULT true,
    pode_criar_usuario BOOLEAN NOT NULL DEFAULT false,
    pode_criar_link BOOLEAN NOT NULL DEFAULT false,
    pode_simular_visao BOOLEAN DEFAULT false,
    limite_criacao_usuarios INT NULL,
    criado_por_usuario_id BIGINT NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    token_versao INT NOT NULL DEFAULT 1,
    foto_perfil TEXT NULL,
    paginas_permitidas JSON NULL,
    pode_cadastrar_escola BOOLEAN DEFAULT false,
    data_expiracao_login DATE NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

my_cur.execute("""
CREATE TABLE IF NOT EXISTS usuario_acesso (
    id_acesso BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_usuario BIGINT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    sigla_uniao VARCHAR(50) NULL,
    sigla_associacao VARCHAR(50) NULL,
    id_escolas INT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_escolas) REFERENCES escolas_pluraal(id_escolas) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

my_cur.execute("""
CREATE TABLE IF NOT EXISTS powerbi_link (
    id_link BIGINT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    link TEXT NOT NULL,
    descricao TEXT NULL,
    ativo BOOLEAN NOT NULL DEFAULT true,
    criado_por_usuario_id BIGINT NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

my_cur.execute("""
CREATE TABLE IF NOT EXISTS usuario_powerbi (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_usuario BIGINT NOT NULL,
    id_link BIGINT NOT NULL,
    atribuido_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atribuido_por_usuario_id BIGINT NULL,
    UNIQUE KEY uq_user_link (id_usuario, id_link),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_link) REFERENCES powerbi_link(id_link) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

# Insert escolas into MySQL
for e in escolas:
    my_cur.execute("""
        INSERT INTO escolas_pluraal (id_escolas, ESCOLA, UNIAO, SIGLA_UNIAO, ASSOCIACAO, SIGLA_ASSOCIACAO)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            ESCOLA=VALUES(ESCOLA), UNIAO=VALUES(UNIAO), SIGLA_UNIAO=VALUES(SIGLA_UNIAO),
            ASSOCIACAO=VALUES(ASSOCIACAO), SIGLA_ASSOCIACAO=VALUES(SIGLA_ASSOCIACAO);
    """, (e["id_escolas"], e["ESCOLA"], e["UNIAO"], e["SIGLA_UNIAO"], e["ASSOCIACAO"], e["SIGLA_ASSOCIACAO"]))

# Insert users into MySQL
for u in users:
    is_master = (u["hierarquia"] == "Master")
    created_dt = u["criado_em"].strftime('%Y-%m-%d %H:%M:%S') if u["criado_em"] else '2026-01-01 00:00:00'
    my_cur.execute("""
        INSERT INTO usuario (
            id_usuario, nome_completo_usuario, email, senha, hierarquia,
            ativo, trocar_senha_no_primeiro_acesso, pode_criar_usuario, pode_criar_link,
            pode_simular_visao, limite_criacao_usuarios, criado_por_usuario_id,
            criado_em, token_versao, foto_perfil, paginas_permitidas,
            pode_cadastrar_escola, data_expiracao_login
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s
        ) ON DUPLICATE KEY UPDATE
            nome_completo_usuario=VALUES(nome_completo_usuario),
            email=VALUES(email),
            senha=VALUES(senha),
            hierarquia=VALUES(hierarquia),
            pode_criar_link=VALUES(pode_criar_link);
    """, (
        u["id_usuario"], u["nome_completo_usuario"], u["email"], u["senha"], u["hierarquia"],
        u["ativo"], u["trocar_senha_no_primeiro_acesso"], u["pode_criar_usuario"], is_master,
        u["pode_simular_visao"], u["limite_criacao_usuarios"], u["criado_por_usuario_id"],
        created_dt, u["token_versao"], u["foto_perfil"], json.dumps(["bi"]),
        u["pode_cadastrar_escola"], u["data_expiracao_login"]
    ))

# Insert initial powerbi links into MySQL
my_link_ids = []
for dash in dashboards_initial:
    my_cur.execute("SELECT id_link FROM powerbi_link WHERE nome = %s;", (dash["nome"],))
    found = my_cur.fetchone()
    if found:
        my_link_ids.append(found[0])
    else:
        my_cur.execute("""
            INSERT INTO powerbi_link (nome, link, descricao, ativo, criado_por_usuario_id)
            VALUES (%s, %s, %s, true, 1);
        """, (dash["nome"], dash["link"], f"Dashboard Power BI {dash['nome']}"))
        my_link_ids.append(my_cur.lastrowid)

for u in users:
    uid = u["id_usuario"]
    if u["hierarquia"] == "Master":
        for lid in my_link_ids:
            my_cur.execute("""
                INSERT IGNORE INTO usuario_powerbi (id_usuario, id_link, atribuido_por_usuario_id)
                VALUES (%s, %s, 1);
            """, (uid, lid))
    elif uid == 78:
        for lid in my_link_ids[:2]:
            my_cur.execute("""
                INSERT IGNORE INTO usuario_powerbi (id_usuario, id_link, atribuido_por_usuario_id)
                VALUES (%s, %s, 1);
            """, (uid, lid))

mysql_conn.commit()
mysql_conn.close()
print("MySQL migration completed successfully!")
