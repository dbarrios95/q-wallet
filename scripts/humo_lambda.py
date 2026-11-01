#!/usr/bin/env python3
"""Prueba de humo de una imagen de Lambda sin AWS (EVD-3-15).

Hace de "Runtime API" de Lambda en 127.0.0.1:<puerto>: entrega UNA invocación (GET /me
sin token) al runtime real de la imagen y espera su respuesta. Comprueba que:
  - el runtime de la imagen arranca (aunque se le quitaron npm y el SDK que trae AWS),
  - el handler empaquetado carga sin módulos faltantes,
  - responde 401 "no_autenticado" con cabeceras de seguridad (CTRL-13, CTRL-18).
Uso: python3 scripts/humo_lambda.py <puerto> <servicio>   (sale con 0 si todo bien)
"""
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

PUERTO, SERVICIO = int(sys.argv[1]), sys.argv[2]
EVENTO = {
    "httpMethod": "GET",
    "resource": "/me",
    "path": "/me",
    "headers": {},
    "queryStringParameters": None,
    "pathParameters": None,
    "body": None,
    "isBase64Encoded": False,
    "requestContext": {"requestId": "humo-0001"},
}
resultado = {}
listo = threading.Event()
entregado = False


class Api(BaseHTTPRequestHandler):
    # El cliente nativo del runtime espera HTTP/1.1 con conexión persistente y las
    # cabeceras completas de la Runtime API (incluida la de trazas).
    protocol_version = "HTTP/1.1"
    def log_message(self, formato, *a):
        print(f"{SERVICIO}: runtime pidió {self.command} {self.path}", file=sys.stderr, flush=True)

    def do_GET(self):
        global entregado
        if self.path.endswith("/runtime/invocation/next") and not entregado:
            entregado = True
            cuerpo = json.dumps(EVENTO).encode()
            self.send_response(200)
            self.send_header("Lambda-Runtime-Aws-Request-Id", "humo-0001")
            self.send_header("Lambda-Runtime-Deadline-Ms", "9999999999999")
            self.send_header("Lambda-Runtime-Invoked-Function-Arn", f"arn:aws:lambda:us-east-1:000000000000:function:qwallet-{SERVICIO}")
            self.send_header("Lambda-Runtime-Trace-Id", "Root=1-00000000-000000000000000000000000;Parent=0000000000000000;Sampled=0")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
        else:
            # Segunda espera del runtime: no hay más eventos; se deja colgada hasta terminar.
            listo.wait(30)
            self.send_response(410)
            self.send_header("Content-Length", "0")
            self.end_headers()

    def do_POST(self):
        largo = int(self.headers.get("Content-Length", 0))
        datos = self.rfile.read(largo).decode() if largo else ""
        resultado["ruta"] = self.path
        resultado["cuerpo"] = datos
        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"{}")
        listo.set()


from http.server import ThreadingHTTPServer
servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), Api)
threading.Thread(target=servidor.serve_forever, daemon=True).start()
if not listo.wait(60):
    print(f"{SERVICIO}: FALLA (el runtime no respondió en 60 s)", flush=True)
    os._exit(1)

ok = False
if resultado.get("ruta", "").endswith("/response"):
    r = json.loads(resultado["cuerpo"])
    cuerpo = json.loads(r.get("body") or "{}")
    cab = r.get("headers", {})
    ok = r.get("statusCode") == 401 and cuerpo.get("error") == "no_autenticado" and cab.get("X-Content-Type-Options") == "nosniff"
    print(f"{SERVICIO}: statusCode={r.get('statusCode')} error={cuerpo.get('error')} correlationId={cuerpo.get('correlationId')} "
          f"cabeceras={sorted(k for k in cab if k.startswith(('X-', 'Strict', 'Cache', 'Content-Security')))}")
else:
    print(f"{SERVICIO}: el runtime reportó un error: {resultado.get('cuerpo', '')[:300]}")
print(f"{SERVICIO}: {'PASA' if ok else 'FALLA'}")
# Salida inmediata: un hilo del servidor puede seguir escribiendo en stderr y, con sys.exit,
# Python abortaba al cerrar ("could not acquire lock for <stderr>") aunque la prueba pasara.
sys.stdout.flush()
sys.stderr.flush()
os._exit(0 if ok else 1)
