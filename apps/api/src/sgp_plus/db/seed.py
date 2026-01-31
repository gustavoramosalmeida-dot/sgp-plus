"""Database seed script"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session

from sgp_plus.db.session import SessionLocal
from sgp_plus.db.models.user import User
from sgp_plus.db.models.role import Role
from sgp_plus.db.models.permission import Permission
from sgp_plus.core.config import settings
from sgp_plus.core.security import hash_password

INSECURE_PASSWORDS = frozenset({"", "admin123", "CHANGE_ME"})


def _block_insecure_bootstrap(*, password: str, email: str) -> None:
    """Impede criação de admin com senha/email inseguros."""
    if (password or "").strip() in INSECURE_PASSWORDS:
        raise RuntimeError(
            "Bootstrap admin com senha insegura ou padrão. "
            "Defina BOOTSTRAP_ADMIN_PASSWORD no .env com valor forte (não use admin123 nem CHANGE_ME)."
        )


def seed():
    """Seed database with initial data"""
    db: Session = SessionLocal()

    try:
        # Create permissions
        permissions_data = [
            {"id": "rbac.manage", "code": "rbac.manage", "name": "Manage RBAC"},
            {"id": "users.read", "code": "users.read", "name": "Read Users"},
            {"id": "users.write", "code": "users.write", "name": "Write Users"},
        ]

        for perm_data in permissions_data:
            perm = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
            if not perm:
                perm = Permission(**perm_data)
                db.add(perm)
                print(f"Created permission: {perm_data['code']}")

        db.commit()

        # Create admin role
        admin_role = db.query(Role).filter(Role.code == "admin").first()
        if not admin_role:
            admin_role = Role(id="admin", code="admin", name="Administrator")
            db.add(admin_role)
            db.flush()

            # Assign all permissions to admin role
            all_perms = db.query(Permission).all()
            admin_role.permissions = all_perms
            print("Created admin role with all permissions")

        db.commit()

        # Create admin user (bloquear senhas previsíveis)
        _block_insecure_bootstrap(
            password=settings.bootstrap_admin_password,
            email=settings.bootstrap_admin_email,
        )

        admin_user = db.query(User).filter(User.email == settings.bootstrap_admin_email).first()
        if not admin_user:
            try:
                password_hash = hash_password(settings.bootstrap_admin_password)
            except ValueError as e:
                # Distinguir entre erro de 72 bytes vs erro de backend
                error_msg = str(e)
                if "72 bytes" in error_msg or "too long" in error_msg.lower():
                    raise RuntimeError(
                        f"BOOTSTRAP_ADMIN_PASSWORD excede o limite de 72 bytes (UTF-8) do bcrypt. "
                        f"Use uma senha mais curta. Detalhes: {e}"
                    ) from e
                else:
                    # Erro de backend/versionamento
                    raise RuntimeError(
                        f"Erro ao processar senha: {error_msg}. "
                        f"Verifique compatibilidade: bcrypt>=4.3.0,<5 é necessário com passlib==1.7.4. "
                        f"Se usar bcrypt>=5, ele é incompatível com passlib 1.7.4 — use bcrypt<5."
                    ) from e
            except Exception as e:
                # Outros erros de backend (ex: AttributeError ao acessar bcrypt.__about__)
                error_type = type(e).__name__
                if "bcrypt" in str(e).lower() or "passlib" in str(e).lower():
                    raise RuntimeError(
                        f"Erro de backend ao processar senha ({error_type}): {e}. "
                        f"Verifique compatibilidade: bcrypt>=4.3.0,<5 é necessário com passlib==1.7.4. "
                        f"Se usar bcrypt>=5, ele é incompatível com passlib 1.7.4 — use bcrypt<5."
                    ) from e
                raise
            admin_user = User(
                email=settings.bootstrap_admin_email,
                password_hash=password_hash,
                is_active=True,
            )
            db.add(admin_user)
            db.flush()

            # Assign admin role
            admin_user.roles = [admin_role]
            print(f"Created admin user: {settings.bootstrap_admin_email}")

        db.commit()
        print("✅ Seed completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
