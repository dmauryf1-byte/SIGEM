// Migra la BD de desarrollo y prepara el usuario "e2e" (Vendedor) con una contraseña aleatoria por corrida
import { execFileSync } from 'node:child_process';
import { randomBytes } from 'node:crypto';

const SEED = `
import os
from app.core.clock import utcnow
from app.core.db import SessionLocal
from app.modules.auth import service as auth
from app.modules.users import service as users
from app.modules.users.models import Role

password = os.environ["E2E_PASSWORD"]
with SessionLocal() as session:
    if users.get_by_username(session, "e2e") is None:
        users.create_user(session, username="e2e", full_name="Prueba E2E", password=password, role=Role.SELLER)
    else:
        auth.reset_password(session, "e2e", password, utcnow())
`;

export default function globalSetup() {
  process.env.E2E_PASSWORD = randomBytes(18).toString('base64url');
  const backend = ['run', '--directory', '../backend'];
  execFileSync('uv', [...backend, 'alembic', 'upgrade', 'head'], { stdio: 'inherit' });
  execFileSync('uv', [...backend, 'python', '-c', SEED], { stdio: 'inherit', env: process.env });
}
