#!/usr/bin/env python3
"""Bloque 7: crea el usuario de prueba de Cognito para CA-07 (login real en el emulador).

Se corre UNA vez, a mano, en AWS CloudShell (us-east-1), igual que el bootstrap:
    pip3 install --user --quiet pycognito==2024.5.1
    python3 usuario_prueba.py

Qué hace:
  1. Busca el user pool "qwallet-usuarios", el cliente "qwallet-app-android" y el dominio
     del login administrado (valores públicos que van en la app).
  2. Crea un usuario nuevo con correo de dominio reservado (qwallet.example, no recibe
     correos), sin enviar invitación, con el correo marcado como verificado y una
     contraseña aleatoria permanente.
  3. Inicia sesión una vez con SRP (el único flujo directo que permite el cliente) y
     responde el reto MFA_SETUP: asocia un TOTP, lo verifica con un código calculado
     aquí y termina el registro del MFA. Revoca el refresh token que sale de esa sesión.
  4. Imprime el correo, la contraseña y la semilla TOTP para guardarlos como secretos
     de GitHub Actions. No se escriben en ningún archivo.

No cambia la configuración del pool ni del cliente y no borra nada. Si se corre otra
vez, crea otro usuario (el anterior queda; se puede deshabilitar después).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import string
import struct
import sys
import time
from datetime import datetime, timezone

import boto3
from pycognito.aws_srp import AWSSRP

REGION = "us-east-1"
POOL = "qwallet-usuarios"
CLIENTE = "qwallet-app-android"


def totp(semilla_b32: str, paso: int | None = None) -> str:
    """RFC 6238: SHA-1, 6 dígitos, 30 segundos (lo que usa Cognito)."""
    clave = base64.b32decode(semilla_b32 + "=" * (-len(semilla_b32) % 8))
    contador = int(time.time() // 30) if paso is None else paso
    h = hmac.new(clave, struct.pack(">Q", contador), hashlib.sha1).digest()
    o = h[-1] & 0x0F
    return f"{(struct.unpack('>I', h[o:o + 4])[0] & 0x7FFFFFFF) % 1_000_000:06d}"


def clave_aleatoria() -> str:
    # Solo letras, números y - _ . : se escriben sin problema con "adb shell input text".
    base = string.ascii_letters + string.digits
    cuerpo = "".join(secrets.choice(base) for _ in range(20))
    return f"Qw{cuerpo}-_.9a"


def main() -> int:
    idp = boto3.client("cognito-idp", region_name=REGION)

    pools = [p for p in idp.list_user_pools(MaxResults=60)["UserPools"] if p["Name"] == POOL]
    if len(pools) != 1:
        print(f"No encontré un único user pool llamado {POOL}.")
        return 1
    pool_id = pools[0]["Id"]
    dominio = idp.describe_user_pool(UserPoolId=pool_id)["UserPool"].get("Domain")
    clientes = [c for c in idp.list_user_pool_clients(UserPoolId=pool_id, MaxResults=60)["UserPoolClients"]
                if c["ClientName"] == CLIENTE]
    if len(clientes) != 1 or not dominio:
        print("No encontré el cliente de la app o el dominio del login administrado.")
        return 1
    client_id = clientes[0]["ClientId"]

    correo = f"ca07-{datetime.now(timezone.utc):%Y%m%d%H%M}@qwallet.example"
    clave = clave_aleatoria()
    print(f"Creando el usuario de prueba {correo} ...")
    idp.admin_create_user(
        UserPoolId=pool_id,
        Username=correo,
        UserAttributes=[{"Name": "email", "Value": correo}, {"Name": "email_verified", "Value": "true"}],
        MessageAction="SUPPRESS",
    )
    idp.admin_set_user_password(UserPoolId=pool_id, Username=correo, Password=clave, Permanent=True)

    # Inicio de sesión con SRP: la contraseña nunca viaja, solo la prueba SRP.
    srp = AWSSRP(username=correo, password=clave, pool_id=pool_id, client_id=client_id, client=idp)
    params = srp.get_auth_params()
    r = idp.initiate_auth(AuthFlow="USER_SRP_AUTH", AuthParameters=params, ClientId=client_id)
    r = idp.respond_to_auth_challenge(
        ClientId=client_id,
        ChallengeName="PASSWORD_VERIFIER",
        ChallengeResponses=srp.process_challenge(r["ChallengeParameters"], params),
    )
    if r.get("ChallengeName") != "MFA_SETUP":
        print(f"Se esperaba el reto MFA_SETUP y llegó: {r.get('ChallengeName')}")
        return 1

    asociado = idp.associate_software_token(Session=r["Session"])
    semilla = asociado["SecretCode"]
    v = idp.verify_software_token(Session=asociado["Session"], UserCode=totp(semilla),
                                  FriendlyDeviceName="ca07-emulador")
    if v.get("Status") != "SUCCESS":
        print(f"No se pudo verificar el TOTP: {v.get('Status')}")
        return 1
    fin = idp.respond_to_auth_challenge(
        ClientId=client_id, ChallengeName="MFA_SETUP", Session=v["Session"],
        ChallengeResponses={"USERNAME": correo},
    )
    tokens = fin.get("AuthenticationResult", {})
    if "RefreshToken" in tokens:
        idp.revoke_token(Token=tokens["RefreshToken"], ClientId=client_id)
    print("MFA TOTP registrado y sesión de configuración revocada.\n")

    print("=" * 70)
    print("Valores PÚBLICOS (cópialos al chat de Claude, van en la app):")
    print(f"   COGNITO_HOST      = {dominio}.auth.{REGION}.amazoncognito.com")
    print(f"   COGNITO_CLIENT_ID = {client_id}")
    print()
    print("SECRETOS (NO los pegues en el chat). En GitHub: Settings > Secrets and")
    print("variables > Actions > New repository secret, uno por uno:")
    print(f"   QWALLET_PRUEBA_CORREO = {correo}")
    print(f"   QWALLET_PRUEBA_CLAVE  = {clave}")
    print(f"   QWALLET_PRUEBA_TOTP   = {semilla}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
