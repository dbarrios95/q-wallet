# Guion de la presentación final: recorrido por la app (sábado 28-nov-2026)

> **Versión vigente: 27-nov-2026** (aprobada por Daniel). Es la sección «Speech por pantalla (versión final)» al inicio. Lo que sigue después de esa sección es la versión del 25-nov y queda solo como referencia.

## Speech por pantalla (versión final, 27-nov-2026)

Reparto: Daniel (apertura, bienvenida, inicio de sesión, desbloqueo y cierre), Katherine (inicio, movimientos y presupuestos), Aroldo (transferir, perfil y el hallazgo). Unos 10 minutos. En cada pantalla: qué se diseñó e implementó (para entenderlo, no se lee) y qué decir.

### Apertura · Daniel (~30 s)
"Buenas tardes. Les presentamos Q-Wallet, una billetera digital para Android que maneja quetzales y funciona en la nube de Amazon. Nuestro papel fue ser los arquitectos de seguridad: la diseñamos segura desde el principio y después la atacamos para comprobar que cada protección funcionara de verdad. Les vamos a mostrar la app pantalla por pantalla. En cada una les contamos qué la protege y cómo lo probamos."

### 1. Bienvenida · Daniel (~40 s)
- Diseño e implementación: freeRASP vigila el teléfono desde que abre la app (root, emulador, herramientas de manipulación) y la bloquea si detecta algo; la app solo habla con los servidores de Amazon que trae grabados (pinning).
- Qué decir: "Esta es la pantalla de bienvenida. Parece simple, pero desde que la app abre ya hay dos protecciones trabajando. La primera revisa el teléfono: si está modificado o si alguien intenta meterse en la app mientras corre, la app se bloquea sola. La segunda cuida la conexión: la app solo habla con los servidores de Amazon que conoce. Si alguien se pone en medio para espiar, la app corta la comunicación. Esta segunda protección nos dio una sorpresa que Aroldo les va a contar al final."

### 2. Inicio de sesión · Daniel (~1 min)
- Diseño e implementación: la contraseña se escribe en la página de Amazon Cognito, no en la app; segundo factor obligatorio (código de 6 dígitos); PKCE para que el código de regreso no sirva si lo interceptan.
- Mostrar: tocar «Iniciar sesión» y que se vea la página de Amazon con correo, contraseña y código.
- Qué decir: "Para entrar, la app no nos pide la contraseña: nos manda a la página de inicio de sesión de Amazon. Lo hicimos así a propósito. Si alguien copiara nuestra app para engañar a la gente, igual no podría robar contraseñas, porque nunca pasan por la app. Además, el segundo factor es obligatorio: no basta con saber la contraseña, también hay que tener el teléfono con la app de códigos. Esto lo probamos con un inicio de sesión real con un usuario de prueba. La lección aquí es no inventar un inicio de sesión propio, sino usar un servicio probado y siempre con doble factor."

### 3. Desbloqueo · Daniel (~1 min)
- Diseño e implementación: huella o PIN del teléfono; permiso de acceso de 15 minutos solo en memoria; permiso de renovación cifrado con una llave del teléfono (Keystore) que solo se abre con la huella o el bloqueo (sin bloqueo no se guarda); sin capturas ni grabación.
- Ojo: proyectada desde un teléfono, sale en negro (FLAG_SECURE).
- Qué decir: "Cuando uno vuelve a la app, pide la huella o el PIN del teléfono. Si la están viendo en negro en la proyección, no es una falla: la pantalla no deja tomar capturas ni grabarla. Lo importante es dónde queda guardada la sesión. El permiso para usar la app dura solo 15 minutos y nunca se escribe en el teléfono. El permiso para renovarla sí se guarda, pero cifrado con una llave del propio teléfono que solo se abre con la huella o el bloqueo. Para probarlo, tomamos un teléfono con permisos de administrador y buscamos la sesión en todos los archivos de la app: no encontramos nada legible. Si a alguien le roban el teléfono, no se llevan la sesión."
- Pase: "Ya entramos. Katherine les explica qué pasa detrás de las pantallas."

### 4. Inicio (saldo) · Katherine (~1 min)
- Diseño e implementación: la pantalla usa datos de ejemplo (conectarla está en el roadmap; la API ya existe y está probada); toda solicitud a la API necesita el permiso de Cognito; solo TLS 1.3; base de datos cifrada con llave propia.
- Qué decir: "Esta es la pantalla principal, con el saldo y los últimos movimientos. Lo decimos de una vez: estos datos todavía son de ejemplo. Conectar esta pantalla es el siguiente paso, y la parte de la nube que la va a alimentar ya está construida y probada. Esa parte funciona con una idea que se llama 'confianza cero': nadie es de confianza por defecto, ni siquiera alguien que ya está adentro. Cada solicitud tiene que traer su permiso, y sin permiso el servidor responde que no. Toda la comunicación va cifrada con la versión más nueva del estándar, y la información en la base de datos también está cifrada, con una llave que controlamos nosotros. Para comprobarlo, escaneamos el servidor desde internet como lo haría un atacante. Solo encontramos una puerta abierta, la que debe estar, y ninguna alerta grave."

### 5. Movimientos · Katherine (~1 min)
- Diseño e implementación: menor privilegio (cada parte solo toca sus tablas); el servidor no le cree a la app qué cuenta es.
- Qué decir: "Aquí está el historial de movimientos. El riesgo más común en este tipo de apps es que alguien cambie un número en la solicitud y termine viendo los movimientos de otra persona. Por eso el servidor nunca le cree a la app cuál es la cuenta: lo averigua él mismo con el permiso del usuario. Además, el sistema está dividido en cinco partes, y cada una solo tiene acceso a sus propias tablas, nada más. Lo probamos tratando de leer los movimientos de otro usuario, y el servidor lo rechazó. También corrimos las 18 pruebas de la lista de riesgos de APIs de OWASP, que es la referencia internacional, y todas quedaron bloqueadas."

### 6. Presupuestos · Katherine (~1 min)
- Diseño e implementación: presupuestos con alerta al pasarse (datos de ejemplo); se aprovecha para contar el flujo DevSecOps y la operación (WAF y SIEM).
- Qué decir: "Esta es la pantalla de presupuestos, que avisa cuando uno se pasa de lo planeado. La aprovecho para contarles dos cosas que no se ven en la app. La primera es cómo se construye: cada vez que cambiamos el código, GitHub hace seis revisiones automáticas. Busca errores de seguridad, librerías con fallas conocidas, contraseñas olvidadas en el código y problemas en la configuración de la nube. Si encuentra algo grave, el cambio no entra. Dos veces nos detuvo sin que hubiéramos tocado nada, porque salieron fallas nuevas en piezas de otros. La segunda es cómo se vigila. Delante del servidor hay un filtro que detiene ataques web conocidos: le lanzamos nueve ataques y bloqueó los nueve. Y hay un sistema que revisa los registros y avisa por correo cuando algo raro pasa. En la prueba, el aviso llegó en unos seis minutos. De hecho, ayer, mientras tomábamos las capturas para el informe, se dispararon dos de esas alarmas." (La última frase solo si llegaron los correos del 27-nov.)
- Pase: "Ahora vamos a la parte que mueve dinero, que es la que más atacamos."

### 7. Transferir · Aroldo (~1 min 15 s)
- Diseño e implementación: validación de monto, teléfono y nota; PIN de 6 dígitos; sin capturas; en el servidor, bloqueo de 15 minutos al quinto PIN fallido y clave única por transferencia. La pantalla todavía no envía la transferencia: esas reglas se probaron contra el servidor. No hacer la transferencia en vivo.
- Qué decir: "Esta es la pantalla para mandar dinero a otro número de teléfono. Como mueve dinero, tiene varias capas. La primera revisa lo que se escribe, para que no se cuele nada raro. Luego pide un PIN de 6 dígitos para autorizar. Y tampoco deja tomar capturas. En el servidor pusimos dos reglas más. Si alguien intenta adivinar el PIN, al quinto error la cuenta se bloquea 15 minutos. Y cada transferencia lleva una clave única, para que aunque se mande dos veces por error, solo se cobre una. Lo probamos directamente contra el servidor: tratamos de adivinar el PIN y se bloqueó al quinto intento. Mandamos 20 transferencias iguales al mismo tiempo y solo pasó una. La regla aquí es que todo lo que mueve dinero se confirma dos veces y se revisa en el servidor, nunca solo en el teléfono."

### 8. Perfil · Aroldo (~45 s)
- Diseño e implementación: datos de la API real (GET /me), datos personales enmascarados, sin capturas; cerrar sesión borra la sesión y revoca el permiso en Cognito.
- Qué decir: "En el perfil, los datos sí vienen del servidor real, y los datos personales salen ocultos en parte: solo se ve lo necesario. Lo más importante es el botón de cerrar sesión. No solo borra la sesión del teléfono: también le avisa a Amazon que anule el permiso. Así, aunque alguien lo hubiera copiado antes, ya no le sirve. Lo comprobamos, y Amazon confirmó que el permiso quedó anulado."

### 9. El hallazgo que solo apareció atacando · Aroldo (~1 min)
- Mostrar: Figura 13 del informe (pantalla de bloqueo de freeRASP).
- Diseño e implementación: el pinning estaba instalado, pero el fetch de Expo SDK 57 lo esquivaba (HAL-13); corrección con un cliente con pinning y una regla de Semgrep que prohíbe fetch.
- Qué decir: "Les debíamos la sorpresa. La protección de la conexión de la que habló Daniel estaba instalada, configurada y revisada. Aun así, cuando la atacamos de verdad, poniendo un espía en medio, el espía pudo leer la información. La causa era que la forma normal de conectarse de la herramienta con que hicimos la app no pasaba por esa protección. Ningún escáner ni revisión de código lo había detectado. Lo corregimos, agregamos una regla que impide volver a cometer el error, repetimos el ataque, y esta vez la app cortó la conexión. Algo parecido pasó con la protección del teléfono: estaba instalada, pero no arrancaba. Esta es la pantalla que ahora aparece cuando detecta un teléfono manipulado. La lección más importante del proyecto: una protección no cuenta hasta que alguien intenta romperla."

### Cierre · Daniel (~45 s)
"Para resumir: al inicio identificamos 41 amenazas, y 18 eran críticas. Después de aplicar y probar las protecciones con ataques reales, no queda ninguna crítica, y el riesgo total bajó un 65 %. Las pruebas encontraron 17 problemas reales, y cada uno tiene una decisión tomada. Nuestro dictamen es favorable, con tres condiciones antes de salir al público. La primera es dejar encendido siempre el filtro de ataques, que hoy solo prendemos para pruebas por costo. La segunda es ajustar los límites para que, cuando hay demasiadas solicitudes, el sistema pida esperar en lugar de dar error. La tercera es actualizar la herramienta con que se hizo la app antes del 31 de enero. Todo el código y las evidencias están en el repositorio. Muchas gracias; quedamos atentos a sus preguntas."

---

# Versión del 25-nov-2026 (referencia)

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
