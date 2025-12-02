from app.database import engine
from sqlalchemy import text

def main():
    with engine.connect() as conn:
        # Ver en qué DB y usuario estamos
        db_info = conn.execute(
            text("SELECT current_database(), current_user")
        ).fetchall()
        print("DB y usuario:", db_info)

        # Ver las tablas públicas
        rows = conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        ).fetchall()
        print("Tablas en public:")
        for r in rows:
            print("-", r[0])

if __name__ == "__main__":
    main()