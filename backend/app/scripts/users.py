"""Gestión de usuarios por consola (SIGEM-004). La contraseña se pide sin mostrarla.

uv run python -m app.scripts.users create --username admin --full-name "Ana" --role Administrador
uv run python -m app.scripts.users unlock <usuario>
uv run python -m app.scripts.users reset-password <usuario>
"""

import argparse
import sys
from collections.abc import Callable, Sequence
from getpass import getpass

from sqlalchemy.orm import Session

from app.core.clock import utcnow
from app.core.db import SessionLocal
from app.core.errors import AppError
from app.modules.auth import service as auth_service
from app.modules.users import service
from app.modules.users.models import Role


def ask_new_password(prompt: Callable[[str], str] = getpass) -> str:
    password = prompt("Contraseña nueva (mínimo 12 caracteres): ")
    if password != prompt("Repite la contraseña: "):
        raise AppError(422, "password_mismatch", "Las contraseñas no coinciden")
    return password


def run(
    argv: Sequence[str],
    session_factory: Callable[[], Session] = SessionLocal,
    prompt: Callable[[str], str] = getpass,
) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.scripts.users")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create", help="Crear un usuario")
    create.add_argument("--username", required=True)
    create.add_argument("--full-name", required=True)
    create.add_argument("--role", choices=[r.value for r in Role], required=True)
    unlock = commands.add_parser("unlock", help="Desbloquear una cuenta bloqueada por intentos")
    unlock.add_argument("username")
    reset = commands.add_parser(
        "reset-password", help="Poner contraseña nueva, desbloquear y cerrar sus sesiones"
    )
    reset.add_argument("username")
    args = parser.parse_args(argv)

    try:
        with session_factory() as session:
            if args.command == "create":
                user = service.create_user(
                    session,
                    username=args.username,
                    full_name=args.full_name,
                    password=ask_new_password(prompt),
                    role=Role(args.role),
                )
                print(f"Usuario '{user.username}' creado con rol {user.role.value}.")
            elif args.command == "unlock":
                user = service.unlock_user(session, args.username)
                print(f"Usuario '{user.username}' desbloqueado.")
            else:
                if service.get_by_username(session, args.username) is None:
                    raise AppError(404, "user_not_found", "El usuario no existe")
                user = auth_service.reset_password(
                    session, args.username, ask_new_password(prompt), utcnow()
                )
                print(f"Contraseña de '{user.username}' cambiada; sus sesiones se cerraron.")
    except AppError as exc:
        print(f"Error: {exc.message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
