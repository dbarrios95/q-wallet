# Guion de la presentación final: recorrido por la app (sábado 28-nov-2026)

> Decisión de Daniel (25-nov-2026): la presentación es un recorrido por la app funcionando, pantalla por pantalla, contando qué protege cada una, cómo lo probamos y qué buena práctica sigue. No se hacen transferencias ni ataques en vivo. Las diapositivas de Claude Slides quedan como respaldo.
> Duración: unos 10 minutos. Cifras tomadas del informe final (`Informe_Final_QWallet.docx`).

## Reparto

| Parte | Pantallas | Expone | Tiempo |
|---|---|---|---|
| 1 | Apertura, Bienvenida, Inicio de sesión, Desbloqueo | Daniel | ~3 min 15 s |
| 2 | Inicio (saldo), Movimientos, Presupuestos | Katherine | ~3 min |
| 3 | Transferir, Perfil, pantalla de bloqueo de freeRASP | Aroldo | ~3 min |
| 4 | Cierre y dictamen | Daniel | ~45 s |

La persona que expone dice el texto; Daniel maneja el teléfono. Una sola idea por pantalla.

## Antes de empezar (checklist)

1. Usar la **misma versión de la app** con la que se tomaron las capturas. El APK de producción se cierra solo en un emulador o en un teléfono con root (freeRASP): eso es correcto, pero arruina la demo.
2. **Iniciar sesión una vez antes** y tener a mano la app de códigos (MFA) del usuario de prueba, por si hay que volver a entrar.
3. **Ojo con compartir pantalla:** las pantallas de Desbloqueo, Transferir y Perfil se ven **en negro** si se proyectan o graban (FLAG_SECURE). No es una falla: es la protección. Tener abiertas las capturas de respaldo (Figura 11 del informe: «en pantalla» frente a «captura») para mostrar cómo se ve en el teléfono.
4. Tener el PDF de las diapositivas abierto por si algo falla.
5. Ensayar una vez con cronómetro.

---

## Parte 1. Daniel

### Apertura (~30 s)
Buenas tardes. Les vamos a presentar Q-Wallet, una billetera digital para Android que maneja quetzales y funciona sobre Amazon Web Services. Nuestro papel fue el de arquitectos de seguridad: la construimos segura desde el diseño y después la atacamos para comprobar que cada protección funcionaba. En vez de diapositivas, vamos a recorrer la app pantalla por pantalla. En cada una les contamos qué la protege, cómo lo probamos y qué buena práctica aplicamos.

### Bienvenida (~40 s)
**Qué se ve:** la portada de la app.
**Qué la protege:** desde que la app arranca, aunque todavía no se ve nada, ya trabajan dos protecciones:
- **freeRASP** revisa si el teléfono tiene root, si es un emulador o si alguien está metiendo herramientas para manipular la app. Si encuentra algo, bloquea la app.
- La app solo habla con servidores que tengan **las llaves de Amazon que trae grabadas**. A esto se le llama *pinning* («fijar el certificado»): si alguien se pone en medio de la conexión con un certificado falso, la app corta la comunicación.

**Cómo lo probamos:** pusimos un interceptor de tráfico en medio, y así encontramos nuestro hallazgo más importante. Aroldo lo cuenta al final.

### Inicio de sesión (~1 min)
**Qué se ve:** al tocar «Iniciar sesión», la app nos manda a una página de Amazon Cognito; ahí van el correo, la contraseña y el código de 6 dígitos de la app de autenticación.
**Qué la protege:**
- **La contraseña nunca pasa por nuestra app.** Se escribe en la página de Cognito, que es el servicio de identidad de Amazon. Así, aunque alguien copiara nuestra app, no podría robar contraseñas.
- **Segundo factor obligatorio (MFA):** no basta con robar la contraseña, también hace falta el teléfono del usuario.
- La app usa un sistema llamado **PKCE**: aunque alguien intercepte el código de regreso, no le sirve sin un secreto que solo conoce esta instalación de la app.

**Cómo lo probamos:** iniciamos sesión de verdad con un usuario de prueba, desde un emulador en GitHub Actions, y después revisamos los archivos de la app con permisos de administrador (root).
**Buena práctica:** no inventar el inicio de sesión propio; usar un proveedor de identidad probado y siempre con MFA.

### Desbloqueo (~1 min)
**Qué se ve:** al volver a abrir la app, pide la huella o el PIN del teléfono. *(Si se está proyectando, esta pantalla sale en negro: explicarlo.)*
**Qué la protege:**
- El permiso de acceso dura solo **15 minutos** y se guarda únicamente en la memoria, nunca en el disco.
- El permiso largo para renovar la sesión se guarda **cifrado con una llave del propio teléfono** (Android Keystore), y esa llave solo se abre con la huella o el bloqueo del teléfono. Si el teléfono no tiene bloqueo, la app no guarda nada.
- La pantalla **no deja tomar capturas ni grabarla**.

**Cómo lo probamos:** con root buscamos tokens en los archivos y en el registro del sistema: **cero tokens legibles**. Si se roban el teléfono, no se llevan la sesión.

*(Pasa a Katherine)* Ya entramos. Katherine les cuenta qué pasa detrás de cada pantalla.

---

## Parte 2. Katherine

### Inicio, saldo (~1 min)
**Qué se ve:** el saldo y los últimos movimientos.
Lo decimos claro: **el saldo, los movimientos y los presupuestos todavía muestran datos de ejemplo**. La API que los va a servir ya está desplegada y probada, pero conectar estas pantallas está en el plan de trabajo. Lo que sí les mostramos es cómo está protegido el camino de esos datos.
**Qué los protege:**
- **Zero Trust**, que quiere decir «no confiar en nadie por defecto»: cada solicitud a la API tiene que traer el permiso de Cognito. Sin permiso, la respuesta es **401** en las 18 rutas.
- El tráfico va cifrado y la API **solo acepta TLS 1.3**, la versión más reciente; la 1.2 la rechaza.
- En la base de datos todo se guarda **cifrado con una llave propia** en AWS KMS.

**Cómo lo probamos:** escaneamos la API desde internet como lo haría un atacante (Nmap, TLS y ZAP): solo el puerto 443 abierto, solo TLS 1.3 y ninguna alerta alta.

### Movimientos (~1 min)
**Qué se ve:** la lista de movimientos con filtros.
**Qué los protege:** **menor privilegio**. Cada parte del sistema solo puede tocar lo suyo: hay cinco microservicios y cada uno tiene su propio permiso, limitado a sus tablas. Y el servidor nunca confía en el número de cuenta que manda la app: saca al usuario del permiso de Cognito.
**Cómo lo probamos:** con un usuario válido intentamos leer los movimientos de **otra persona**, y el servidor respondió **404 o 403**. Es el ataque número uno de las API según OWASP, y las **18 pruebas** del OWASP API Top 10 quedaron bloqueadas.
**Buena práctica:** la app nunca decide quién es el usuario; lo decide el servidor.

### Presupuestos (~1 min)
**Qué se ve:** presupuestos por categoría y la alerta al pasarse.
Aprovechamos esta pantalla para contar dos cosas que no se ven:
- **Cómo se construye la app.** Cada cambio de código pasa por **seis revisiones automáticas** en GitHub: errores en el código, librerías con fallas conocidas, contraseñas olvidadas en el código, configuración de la nube e imágenes. Si algo grave aparece, el cambio no entra. Nos frenó dos veces **sin que cambiáramos una línea**: cuando se publicaron fallas nuevas en una librería que usamos y cuando la imagen base de Amazon para Lambda amaneció con fallas.
- **Cómo se vigila en operación.** Delante de la API va un **WAF** (un filtro que detiene ataques web conocidos): de 9 ataques lanzados, **bloqueó los 9**. Y un **SIEM** en CloudWatch junta los registros, con 14 reglas y 10 alarmas: en una prueba real, la alerta llegó por correo en **unos 6 minutos**.

*(Pasa a Aroldo)* Ahora vamos a la parte que mueve dinero, que es la que más atacamos.

---

## Parte 3. Aroldo

### Transferir (~1 min 15 s)
**Qué se ve:** el formulario para mandar dinero a un número de teléfono y la ventana que pide el PIN. *(No se hace la transferencia. Si se proyecta, sale en negro.)*
**Qué la protege:**
- **PIN de 6 dígitos** para autorizar. En el servidor, al **quinto intento fallido** la cuenta se bloquea **15 minutos**.
- **Validación estricta** de lo que se escribe: monto, teléfono y nota, en la app y otra vez en el servidor.
- **Sin capturas ni grabación** en esta pantalla.
- **Protección contra el doble cobro:** cada transferencia lleva una clave única.

**Cómo lo probamos:**
- Fuerza bruta del PIN: **bloqueo al quinto intento**.
- **20 transferencias iguales al mismo tiempo**: solo se aplicó **una**.
- Intentamos tomar una captura con la herramienta de Android: **sale negra**.

**Buena práctica:** toda operación que mueve dinero se confirma dos veces y se revisa en el servidor, nunca solo en el teléfono.

### Perfil (~45 s)
**Qué se ve:** los datos del usuario, que vienen de la API real, y el botón «Cerrar sesión segura».
**Qué la protege:**
- Los datos personales salen **enmascarados**: solo se ve lo necesario.
- La pantalla **no permite capturas**.
- **Cerrar sesión no solo borra la sesión del teléfono:** también le avisa a Cognito para que **anule** el permiso. Aunque alguien lo hubiera copiado, ya no sirve.

**Cómo lo probamos:** después de cerrar sesión, Cognito confirmó la anulación (respuesta 200).

### El hallazgo que solo apareció atacando (~1 min) *(mostrar la Figura 13: pantalla de bloqueo de freeRASP)*
La protección de la Bienvenida, la de «fijar el certificado», estaba instalada, configurada y revisada. Aun así, cuando la atacamos con un interceptor, **el interceptor sí pudo leer la información**. La causa: en la versión de Expo que usamos, la forma normal de conectarse a internet no pasaba por esa protección. Ningún escáner ni revisión de código lo había visto. Lo corregimos haciendo que todas las llamadas pasen por la conexión protegida, agregamos una regla que prohíbe la forma insegura y repetimos el ataque: **la app cortó la conexión**.
Lo mismo pasó con freeRASP: estaba instalado, pero no arrancaba. Esta es la pantalla de bloqueo que aparece ahora cuando detecta root o herramientas de manipulación.
**La lección:** un control no cuenta hasta que una prueba intenta romperlo.

*(Pasa a Daniel)*

---

## Parte 4. Daniel: cierre (~45 s)
Para resumir: modelamos **41 amenazas**, de las cuales **18 eran críticas**. Después de aplicar los controles y probarlos con ataques reales, quedan **cero críticas**, y la suma del riesgo bajó de **580 a 202 puntos, un 65 %**. Encontramos **17 hallazgos reales**, y cada uno tiene una decisión.
Nuestro dictamen es **favorable, con tres condiciones antes de salir a producción**: dejar el WAF encendido de forma permanente, ajustar los límites para que una ráfaga de solicitudes reciba «espere» (429) y no un error (500), y actualizar a Expo SDK 58 antes del 31 de enero.
Todo el código, las pruebas y las evidencias están en el repositorio. Gracias; quedamos atentos a sus preguntas.

---

## Preguntas probables y respuesta corta

| Pregunta | Quién | Respuesta |
|---|---|---|
| ¿Por qué el saldo es de ejemplo? | Katherine | La prioridad fue proteger y probar la API y el inicio de sesión reales. La API ya existe y pasó las pruebas; conectar estas pantallas está en el roadmap y no cambia la arquitectura. |
| ¿Qué riesgo aceptaron? | Daniel | RSK-11, la saturación de la API. El WAF permanente cuesta unos US$9 al mes, casi el doble del presupuesto de US$5. Está aceptado por escrito, con dueño, fecha y plan. |
| ¿Qué es HAL-17? | Aroldo | Una ráfaga de usuarios con sesión recibe error 500 en vez de 429, porque se acaba primero el límite de Lambda. Es la segunda condición del dictamen. |
| ¿Por qué no Wazuh? | Katherine | Necesita un servidor encendido con 4 GB de memoria y no cabía en el presupuesto. CloudWatch no tiene servidores propios y cuesta uno o dos dólares al mes. Wazuh quedó en el roadmap. |
| ¿Cómo saben que el riesgo bajó de verdad? | Aroldo | De las 41 amenazas, 31 se comprobaron con un ataque y 6 revisando la configuración desplegada. Las dos parciales las subimos un nivel por honestidad. |
| ¿Cumple con la JM-98-2025? | Daniel | La usamos como referencia de diseño. Q-Wallet, S.A. no es una entidad supervisada por la SIB, así que no afirmamos cumplimiento. |
