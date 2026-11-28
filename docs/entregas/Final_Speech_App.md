# Speech de la presentación final: recorrido por Q-Wallet (sábado 28-nov-2026)

> Versión para decir en voz alta, con lenguaje sencillo. Sale del guion de `Final_Guion_Demo.md` (27-nov) y se ajusta a la app que ya probamos en el teléfono de Daniel: el inicio de sesión va en vivo, el desbloqueo se muestra cerrando y abriendo la app, y se suma lo que encontramos en el ensayo al cerrar sesión.
>
> **Reparto:** Daniel (apertura, bienvenida, inicio de sesión, desbloqueo y cierre), Katherine (inicio, movimientos y presupuestos) y Aroldo (transferir, perfil y el hallazgo). **Duración:** unos 10 minutos. La presentación es **en línea** (videollamada): Daniel comparte la pantalla del teléfono y lo maneja; cada uno habla de sus pantallas. Las indicaciones entre corchetes no se leen.

---

## Quién comparte qué (presentación en línea)

| Quién | Qué tiene abierto | Cuándo comparte |
|---|---|---|
| **Daniel** | La pantalla del teléfono compartida en la llamada. Cámara encendida y, si se puede, apuntando al teléfono. | Toda la presentación, salvo cuando Aroldo comparte. |
| **Katherine** | El informe en PDF por si falla algo (Figura 9: pantallas principales). | Solo si se cae la pantalla de Daniel. Sus pantallas (Inicio, Movimientos y Presupuestos) se ven normal. |
| **Aroldo** | La **Figura 11** del informe (Transferir y Perfil: en el teléfono frente a la captura) o las dos imágenes sueltas: [Transferir en pantalla](https://github.com/dbarrios95/q-wallet/blob/main/docs/evidencias/bloque6/EVD-6-06a_transferir_en_pantalla.png) y [Perfil en pantalla](https://github.com/dbarrios95/q-wallet/blob/main/docs/evidencias/bloque6/EVD-6-07a_perfil_en_pantalla.png). También la **Figura 13** (pantalla de bloqueo). | En Transferir y Perfil, cuando la pantalla de Daniel se pone en negro, y en el hallazgo final (Figura 13). |

**Por qué se ve en negro:** Desbloqueo, Transferir y Perfil no dejan que nada copie la pantalla (FLAG_SECURE). La pantalla compartida en la llamada también es una copia, así que sale en negro. En el teléfono de Daniel se ven normal. Las demás pantallas se ven sin problema.

**Cómo hacer el cambio:** Aroldo dice su frase, comparte su pantalla con la figura, explica y deja de compartir. Daniel vuelve a compartir el teléfono (en Meet y Zoom, si Aroldo deja de compartir, la pantalla de Daniel vuelve sola o hay que darle «Compartir» de nuevo: ensayarlo).

## Antes de empezar

1. En la app: **Perfil → Cerrar sesión**, para que arranque en Bienvenida. Revisar que al tocar «Continuar a la página segura» pida correo, contraseña y código.
2. Teléfono con internet, batería cargada, brillo alto y en modo «No molestar».
3. La app de códigos (Google Authenticator) a la mano, y la contraseña del usuario de la demo guardada en Chrome.
4. Probar la pantalla compartida del teléfono en la llamada: todo se ve menos **Desbloqueo, Transferir y Perfil, que salen en negro**. Es lo esperado y se usa como demostración.
5. Aroldo con la Figura 11 y la Figura 13 abiertas; Katherine con el informe en PDF (Figura 10: inicio de sesión; Figura 9: pantallas principales) por si algo falla.
6. Ensayar una vez el cambio de pantalla compartida entre Daniel y Aroldo.

---

## Daniel

### Apertura (~30 s)
[Teléfono en la pantalla de Bienvenida.]

"Buenas tardes. Les presentamos Q-Wallet, una billetera digital para Android que maneja quetzales y funciona en la nube de Amazon. Nuestro papel fue ser los arquitectos de seguridad: la diseñamos segura desde el principio y después la atacamos para comprobar que cada protección funcionara de verdad. En vez de diapositivas, les vamos a mostrar la app funcionando, pantalla por pantalla. En cada una les contamos qué la protege y cómo lo probamos."

### 1. Bienvenida (~40 s)
"Esta es la pantalla de bienvenida. Parece simple, pero desde que la app abre ya hay dos protecciones trabajando.

La primera revisa el teléfono, con una herramienta que se llama freeRASP y que viene dentro de la app. Si el teléfono está modificado (lo que se conoce como 'root'), si es un teléfono falso de laboratorio o si alguien intenta meterse en la app mientras corre, la app se bloquea sola.

La segunda cuida la conexión, con una técnica que se llama 'pinning' o fijado de certificados, usando la librería react-native-ssl-public-key-pinning. La app trae grabada la identidad de los servidores de Amazon y solo habla con ellos. Si alguien se pone en medio para espiar, la app corta la comunicación. Esta segunda protección nos dio una sorpresa que Aroldo les va a contar al final."

### 2. Inicio de sesión (~1 min 15 s)
[Tocar «Iniciar sesión» → «Continuar a la página segura». Escribir correo y contraseña, y después el código de la app de autenticación. Al terminar, el teléfono pide la huella para guardar la sesión. Se llega a Inicio.]

"Para entrar, fíjense que la app no nos pide la contraseña: nos manda a la página de inicio de sesión de Amazon. Lo hicimos así a propósito. Si alguien copiara nuestra app para engañar a la gente, igual no podría robar contraseñas, porque nunca pasan por la app.

[Mientras escribe el código.] Además, el segundo paso es obligatorio. No basta con saber la contraseña: también hay que tener el teléfono con la app que genera este código de seis números, que cambia cada 30 segundos.

[Cuando pide la huella.] Ahora el teléfono me pide la huella para guardar la sesión. Ya les explico por qué.

La lección aquí es no inventar un inicio de sesión propio, sino usar un servicio probado y siempre con doble paso de verificación."

### 3. Desbloqueo (~1 min)
[Cerrar la app desde recientes y volver a abrirla. Pide la huella. Ponerla y entrar.]

"Ahora cierro la app y la vuelvo a abrir, como haría cualquiera durante el día. Ya no me pide la contraseña: me pide la huella. Fíjense que mi pantalla compartida se puso en negro. No es una falla: esta pantalla no deja que nada la copie, ni una captura, ni una grabación, ni esta transmisión. En mi teléfono la veo normal: un candado y el botón para poner la huella. [Si la cámara apunta al teléfono: 'En mi cámara sí la pueden ver.'] Apenas entre a la app, la imagen vuelve.

Lo importante es dónde queda guardada la sesión. El permiso para usar la app dura solo 15 minutos y nunca se escribe en el teléfono. El permiso para renovarlo sí se guarda, pero encerrado con una llave del propio teléfono que solo se abre con la huella o el bloqueo de pantalla.

Para probarlo, tomamos un teléfono con permisos de administrador y buscamos la sesión en todos los archivos de la app. No encontramos nada legible. Si a alguien le roban el teléfono, no se lleva la sesión."

[Pase.] "Ya entramos. Katherine les explica qué pasa detrás de las pantallas."

---

## Katherine

### 4. Inicio (~1 min)
[Pantalla de Inicio con el saldo.]

"Esta es la pantalla principal, con el saldo, los accesos rápidos y los últimos movimientos. Lo decimos de una vez: estos datos todavía son de ejemplo. Conectar esta pantalla es el siguiente paso, y la parte de la nube que la va a alimentar ya está construida y probada.

Esa parte funciona con una idea que se llama 'confianza cero': nadie es de confianza por defecto, ni siquiera alguien que ya está adentro. Cada solicitud tiene que traer su permiso, y sin permiso el servidor responde que no.

Toda la comunicación va cifrada con la versión más nueva del estándar, y la información guardada también está cifrada, con una llave que controlamos nosotros. Para comprobarlo, revisamos el servidor desde internet como lo haría un atacante. Solo encontramos una puerta abierta, la que debe estar, y ninguna alerta grave."

### 5. Movimientos (~1 min)
[Tocar «Movimientos» en las acciones rápidas o la pestaña «Actividad».]

"Aquí está el historial de movimientos. El riesgo más común en este tipo de apps es que alguien cambie un número en la solicitud y termine viendo los movimientos de otra persona. Por eso el servidor nunca le cree a la app cuál es la cuenta: lo averigua él mismo con el permiso del usuario.

Además, el sistema está dividido en cinco partes, y cada una solo puede tocar su propia información, nada más. Lo probamos tratando de leer los movimientos de otro usuario, y el servidor lo rechazó. También corrimos las 18 pruebas de la lista internacional de riesgos para este tipo de servicios, la de OWASP, y todas quedaron bloqueadas."

### 6. Presupuestos (~1 min)
[Pestaña «Presupuesto».]

"Esta es la pantalla de presupuestos, que avisa cuando uno se pasa de lo planeado. La aprovecho para contarles dos cosas que no se ven en la app.

La primera es cómo se construye. Cada vez que cambiamos el código, GitHub hace seis revisiones automáticas: busca errores de seguridad, piezas de terceros con fallas conocidas, contraseñas olvidadas en el código y problemas en la configuración de la nube. Si encuentra algo grave, el cambio no entra. Dos veces nos detuvo sin que hubiéramos tocado nada, porque salieron fallas nuevas en piezas de otros.

La segunda es cómo se vigila. Delante del servidor hay un filtro que detiene ataques conocidos: le lanzamos nueve ataques y bloqueó los nueve. Y hay un sistema que revisa los registros y avisa por correo cuando pasa algo raro. En la prueba, el aviso llegó en unos seis minutos."

[Pase.] "Ahora vamos a la parte que mueve dinero, que es la que más atacamos."

---

## Aroldo

### 7. Transferir (~1 min 15 s)
[Daniel entra a la pestaña «Transferir» y su pantalla compartida se pone en negro. Aroldo dice la primera frase, comparte la Figura 11 (o la imagen «Transferir en pantalla») y sigue hablando. Daniel puede llenar el formulario y abrir la ventana del PIN, pero **no confirma la transferencia**.]

"Como ven, en cuanto Daniel entró a esta pantalla, su transmisión se puso en negro. No es una falla: aquí no se permite copiar la pantalla, para que ninguna app espía se lleve los datos de la transferencia. Les comparto cómo se ve en el teléfono. [Comparte la figura.] A la izquierda está lo que ve el usuario, y a la derecha lo que obtiene cualquiera que intente capturarla: negro.

Esta es la pantalla para mandar dinero a otro número de teléfono. Como mueve dinero, tiene varias capas más. La primera revisa lo que se escribe, para que no se cuele nada raro. Después pide un PIN de seis números para autorizar.

Esta pantalla todavía no envía la transferencia al servidor. Lo que sí está construido y probado es el servidor que la va a recibir, y ahí pusimos dos reglas más. Si alguien intenta adivinar el PIN, al quinto error la cuenta se bloquea 15 minutos. Y cada transferencia lleva una clave única: aunque se mande dos veces por error, solo se cobra una.

Lo probamos directamente contra el servidor. Tratamos de adivinar el PIN y se bloqueó al quinto intento. Mandamos 20 transferencias iguales al mismo tiempo y solo pasó una.

La regla aquí es que todo lo que mueve dinero se confirma dos veces y se revisa en el servidor, nunca solo en el teléfono."

### 8. Perfil y cierre de sesión (~1 min)
[Aroldo sigue compartiendo la Figura 11, ahora en el par de Perfil (o la imagen «Perfil en pantalla»). Daniel entra a «Perfil», baja hasta «Cerrar sesión segura» y lo toca cuando Aroldo llegue a esa parte. Después Aroldo deja de compartir y Daniel vuelve a compartir el teléfono, que ya está en Bienvenida y se ve normal.]

"El perfil también sale en negro en la transmisión de Daniel, por la misma protección; aquí les muestro cómo se ve en el teléfono. Los datos sí vienen del servidor real, y los datos personales salen ocultos en parte: solo se ve lo necesario.

Lo más importante es este botón de cerrar sesión. No solo borra la sesión del teléfono: también le avisa a Amazon que anule el permiso. Así, aunque alguien lo hubiera copiado antes, ya no le sirve. Lo comprobamos, y Amazon confirmó que el permiso quedó anulado.

Y aquí tenemos algo que encontramos ayer, ensayando esta misma demo. Al cerrar sesión y volver a entrar, la página de Amazon nos dejaba pasar sin pedir contraseña ni código. Era porque el navegador del teléfono todavía recordaba la sesión. O sea, si alguien tomaba el teléfono después de que cerráramos sesión, podía volver a entrar. Lo corregimos: ahora cerrar sesión también cierra la sesión en el navegador. Daniel, ¿podés cerrar sesión? [Daniel lo toca. Aroldo deja de compartir y Daniel vuelve a compartir el teléfono.] Ahí ven que regresó a la bienvenida, y la pantalla de Daniel se ve otra vez, porque esta pantalla no tiene datos delicados."

### 9. El hallazgo que solo apareció atacando (~1 min)
[Aroldo comparte la Figura 13 del informe: pantalla de bloqueo. Al terminar deja de compartir.]

"Ese no fue el único caso. Les debíamos la sorpresa de la que habló Daniel.

La protección de la conexión estaba instalada, configurada y revisada. Aun así, cuando la atacamos de verdad, poniendo un espía en medio, el espía pudo leer la información. La causa era que la forma normal de conectarse de la herramienta con la que hicimos la app no pasaba por esa protección. Ningún revisor automático lo había detectado. Lo corregimos, agregamos una regla que impide volver a cometer el error, repetimos el ataque y esta vez la app cortó la conexión.

Algo parecido pasó con la protección del teléfono: estaba instalada, pero no arrancaba. Esta es la pantalla que ahora aparece cuando detecta un teléfono manipulado.

La lección más importante del proyecto: una protección no cuenta hasta que alguien intenta romperla."

[Pase.] "Daniel les resume los resultados."

---

## Daniel

### Cierre (~45 s)
"Para resumir: al inicio identificamos 41 amenazas, y 18 eran críticas. Después de aplicar las protecciones y probarlas con ataques reales, no queda ninguna crítica, y el riesgo total bajó un 65 %. Las pruebas encontraron 17 problemas reales, y cada uno tiene una decisión tomada.

Nuestro dictamen es favorable, con tres condiciones antes de abrir la app al público. La primera es dejar encendido siempre el filtro de ataques, que hoy solo prendemos para pruebas por costo. La segunda es ajustar los límites para que, cuando lleguen demasiadas solicitudes juntas, el sistema pida esperar en lugar de dar error. La tercera es actualizar la herramienta con la que se hizo la app antes del 31 de enero.

Todo el código y las evidencias están en el repositorio. Muchas gracias; quedamos atentos a sus preguntas."

---

## Si algo falla en vivo

| Qué pasa | Qué hacer y qué decir |
|---|---|
| No hay internet o el inicio de sesión no carga | Mostrar la Figura 10 del informe (inicio de sesión): "La conexión nos falló, pero así se ve la página; lo probamos con un usuario real en las pruebas automáticas." Seguir con la Figura 11 para el desbloqueo. |
| La pantalla compartida sale en negro | En Desbloqueo, Transferir y Perfil es lo esperado: "Esto es la protección contra capturas." Aroldo comparte la Figura 11. Si sale en negro en otra pantalla, cerrar la app desde recientes, abrirla de nuevo y seguir. |
| Se cae la pantalla compartida de Daniel | Katherine comparte el informe (Figura 9 para Inicio, Movimientos y Presupuestos) mientras Daniel vuelve a conectar. |
| El código de seis números falla | Esperar a que cambie (30 s) y escribir el nuevo. Revisar que la hora del teléfono esté en automático. |
| La app se bloquea con la pantalla de seguridad | Era lo que debía pasar si el teléfono parece manipulado: aprovecharlo para la parte 9. |

## Preguntas probables y respuesta corta

| Pregunta | Quién | Respuesta |
|---|---|---|
| ¿Por qué el inicio de sesión se va a la página de Amazon y no es una pantalla de la app? | Daniel | Se podía hacer dentro de la app, pero elegimos que la contraseña nunca la toque. Es lo que recomienda el estándar para apps de teléfono, y nos protege si alguien copia o modifica la app. |
| ¿Por qué no ponen un botón para apagar la protección de capturas durante la demo? | Daniel | Porque un botón así sería una debilidad: cualquiera con el teléfono podría apagarla. Preferimos que se vea en negro, que es justo la prueba de que funciona. |
| ¿El PIN de la transferencia es real? | Aroldo | En la pantalla todavía no se revisa, porque la transferencia no se envía. La revisión del PIN y el bloqueo al quinto intento están en el servidor y se probaron ahí. Conectar la pantalla está en el plan de trabajo. |
| ¿Por qué el saldo es de ejemplo? | Katherine | La prioridad fue proteger y probar el servidor y el inicio de sesión reales. El servidor ya existe y pasó las pruebas; conectar estas pantallas es el siguiente paso y no cambia el diseño. |
| ¿Qué encontraron al final? | Aroldo | Que cerrar sesión no cerraba la sesión del navegador, y se podía volver a entrar sin contraseña. Lo vimos en el ensayo y ya está corregido. |
| ¿Qué riesgo aceptaron? | Daniel | Que el servidor se sature con demasiadas solicitudes. El filtro permanente cuesta unos US$9 al mes, casi el doble del presupuesto de US$5. Está aceptado por escrito, con responsable, fecha y plan. |
| ¿Cómo saben que el riesgo bajó de verdad? | Aroldo | De las 41 amenazas, 31 se comprobaron con un ataque y 6 revisando la configuración ya instalada. Las que quedaron a medias las calificamos un nivel más alto, por honestidad. |
| ¿Cumple con la norma de la Junta Monetaria (JM-98-2025)? | Daniel | La usamos como guía de diseño. Q-Wallet no es una entidad supervisada por la Superintendencia de Bancos, así que no decimos que cumple. |
