// Genera la sección 0 (portada, resumen ejecutivo, índice) y las referencias unificadas de la Entrega 1.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel, PageBreak,
  Header, PageNumber, TabStopType, LeaderType,
} = require('docx');

const OUT = process.argv[2];
const K = parseInt(process.argv[3] || '3', 10); // páginas de la sección 0

const FONT = 'Arial';
const styles = {
  default: { document: { run: { font: FONT, size: 24 }, paragraph: { spacing: { line: 360, before: 0, after: 0 } } } },
  paragraphStyles: [
    { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
      run: { font: FONT, size: 24, bold: true, color: '000000' },
      paragraph: { spacing: { before: 240, after: 120, line: 360 }, alignment: AlignmentType.CENTER, outlineLevel: 0, keepNext: true } },
    { id: 'TOC1', name: 'toc 1', basedOn: 'Normal', next: 'Normal', run: { font: FONT, size: 24 },
      paragraph: { tabStops: [{ type: TabStopType.RIGHT, position: 9360, leader: LeaderType.DOT }] } },
    { id: 'TOC2', name: 'toc 2', basedOn: 'Normal', next: 'Normal', run: { font: FONT, size: 24 },
      paragraph: { indent: { left: 360 }, tabStops: [{ type: TabStopType.RIGHT, position: 9360, leader: LeaderType.DOT }] } },
    { id: 'TOC3', name: 'toc 3', basedOn: 'Normal', next: 'Normal', run: { font: FONT, size: 24 },
      paragraph: { indent: { left: 720 }, tabStops: [{ type: TabStopType.RIGHT, position: 9360, leader: LeaderType.DOT }] } },
  ],
};
const page = { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } };
const header = new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT] })] })] });

const body = (text) => new Paragraph({ alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 720 }, children: [new TextRun(text)] });
const center = (text, opts = {}) => new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text, ...opts })] });
const blank = () => new Paragraph({ children: [] });

// ---------- Portada (APA 7, estudiante) ----------
const portada = [
  blank(), blank(), blank(),
  center('Q-Wallet: seguridad desde el diseño de una billetera digital móvil en la nube de AWS', { bold: true }),
  center('Entrega 1: Selección y Planificación; Activos y Riesgos', { bold: true }),
  blank(),
  center('Katherine Johana Sandoval Monterroso (1493-21-16747)'),
  center('Daniel Edivin Barrios Monzón (1493-19-3305)'),
  center('Aroldo Francisco Lolmet Calel (1493-23-20110)'),
  blank(),
  center('Facultad de Ingeniería en Sistemas, Programa de Postgrados, Universidad Mariano Gálvez de Guatemala'),
  center('Maestría en Seguridad Informática'),
  center('Seguridad en Aplicaciones'),
  center('Osberto Saúl Gallo Orozco'),
  center('17 de octubre de 2026'),
];

// ---------- Resumen ejecutivo ----------
const resumen = [
  new Paragraph({ children: [new PageBreak()] }),
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('Resumen ejecutivo')] }),
  body('Q-Wallet es una billetera digital ficticia para Android, con dinero simulado en quetzales, que funciona sobre servicios de Amazon Web Services: API Gateway, Cognito, Lambda y DynamoDB. En esta primera entrega presentamos la selección y planificación del proyecto y el análisis de activos y riesgos. Trabajamos con un enfoque seguro desde el diseño: construimos la aplicación con sus controles desde el inicio, y las pruebas de las fases siguientes servirán para demostrar que esos controles funcionan.'),
  body('Seguimos el proceso de gestión de riesgos de ISO/IEC 27005:2022. Inventariamos 28 activos de seis tipos según ISO/IEC 27001:2022 y los clasificamos por confidencialidad, integridad y disponibilidad: 11 resultaron de criticidad crítica, 13 alta y 4 media. Modelamos la arquitectura en diagramas de flujo de datos de tres niveles, con seis fronteras de confianza, y aplicamos STRIDE a cada elemento. Identificamos 41 amenazas y justificamos 14 casos no aplicables; la categoría más frecuente fue la divulgación de información, con 13 amenazas, seguida de la manipulación, con 9.'),
  body('Valoramos cada amenaza con DREAD y la convertimos en probabilidad e impacto sobre una matriz de 5 × 5. El riesgo inherente quedó en 18 riesgos críticos, 12 altos, 11 medios y ninguno bajo, repartidos en las siete capas de defensa en profundidad. Para tratarlos definimos 23 controles (CTRL-01 a CTRL-23), entre ellos la autorización a nivel de objeto, el PIN de transacción con bloqueo, la autenticación multifactor con OAuth2 y PKCE, el cifrado con llaves propias de KMS, AWS WAF, la autoprotección de la aplicación en tiempo de ejecución y un SIEM con Wazuh. Decidimos mitigar 39 riesgos, transferir 1 y aceptar 1.'),
  body('Con los controles implementados, el riesgo residual proyectado baja a 0 críticos, 1 alto, 26 medios y 14 bajos, y la suma de los puntajes de riesgo pasa de 580 a 207, una reducción del 64 %. El único riesgo alto que queda, RSK-32 (compromiso del flujo de despliegue), no lo aceptamos: tiene un plan de refuerzo para llevarlo a nivel medio. Esta proyección todavía no está verificada. En las fases siguientes desplegaremos la arquitectura con Terraform y GitHub Actions y ejecutaremos los casos de abuso dentro de la política de pruebas de AWS para medir el riesgo residual real.'),
];

// ---------- Índice ----------
// Páginas medidas al renderizar cada Word (cuerpo sin sus referencias), ensamblado en este orden
// y empezando cada Word en página nueva: 1.1–1.4 = 8 págs., 1.5 = 8 págs., sección 2 = 31 págs.
const A = K, B = K + 8, C = K + 16, R = K + 16 + 31;
const entries = [
  [1, 'Resumen ejecutivo', 2],
  [1, '1. Selección y Planificación', A + 1],
  [2, '1.1 Contexto', A + 1],
  [2, '1.2 Objetivos', A + 2],
  [3, 'Objetivo general', A + 2],
  [3, 'Objetivos específicos', A + 2],
  [2, '1.3 Alcance', A + 4],
  [3, 'Enfoque seguro desde el diseño', A + 5],
  [3, 'Restricciones', A + 5],
  [2, '1.4 Normativas y estándares de referencia', A + 6],
  [2, '1.5 Definición del scope técnico', B + 1],
  [3, '1.5.1 Arquitectura de la solución', B + 1],
  [3, '1.5.2 Superficie de la API', B + 2],
  [3, '1.5.3 Fronteras de confianza', B + 3],
  [3, '1.5.4 Controles de seguridad por componente', B + 4],
  [3, '1.5.5 Herramientas por fase', B + 5],
  [3, '1.5.6 Reglas de enfrentamiento del pentest', B + 5],
  [1, '2. Activos y Riesgos', C + 1],
  [2, '2.1 Inventario de activos', C + 1],
  [2, '2.2 Clasificación CIA y criticidad', C + 7],
  [2, '2.3 Modelado de amenazas STRIDE', C + 9],
  [2, '2.4 Valoración DREAD', C + 17],
  [2, '2.5 Matriz de riesgos inicial', C + 20],
  [3, '2.5.1 Conversión de DREAD a probabilidad e impacto', C + 20],
  [3, '2.5.2 Matriz de riesgos', C + 21],
  [3, '2.5.3 Mapa de calor del riesgo inherente', C + 25],
  [3, '2.5.4 Riesgos por capa de defensa', C + 26],
  [3, '2.5.5 Riesgo residual proyectado y tratamiento', C + 27],
  [1, 'Referencias', R + 1],
];
const indice = [
  new Paragraph({ children: [new PageBreak()] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240, after: 120 }, children: [new TextRun({ text: 'Índice', bold: true })] }),
  ...entries.map(([lvl, t, p], i) => new Paragraph({
    style: `TOC${lvl}`,
    children: [new TextRun({ text: `@@TOC${i}@@` + t }), new TextRun({ text: '\t' + p })],
  })),
];

// ---------- Referencias unificadas ----------
const refs = [
  [['Amazon Web Services. (s. f.-a). '], ['Guatemala: Financial services compliance center', 1], ['. Recuperado el 10 de octubre de 2026, de https://aws.amazon.com/financial-services/security-compliance/compliance-center/gt']],
  [['Amazon Web Services. (s. f.-b). '], ['Penetration testing', 1], ['. Recuperado el 10 de octubre de 2026, de https://aws.amazon.com/security/penetration-testing/']],
  [['Amazon Web Services. (s. f.-c). '], ['Shared responsibility model', 1], ['. https://aws.amazon.com/compliance/shared-responsibility-model/']],
  [['Center for Internet Security. (2024). '], ['CIS Docker Benchmark', 1], [' (versión 1.7.0). https://www.cisecurity.org/benchmark/docker']],
  [['Center for Internet Security. (2025). '], ['CIS Amazon Web Services Foundations Benchmark', 1], [' (versión 5.0). https://www.cisecurity.org/benchmark/amazon_web_services']],
  [['Congreso de la República de Guatemala. (2001). '], ['Decreto Número 67-2001: Ley contra el Lavado de Dinero u Otros Activos', 1], ['. Banco de Guatemala. https://pinfex.banguat.gob.gt/sites/default/files/banguat/leyes/2025/ley_contra_lavado_de_dinero.pdf']],
  [['Congreso de la República de Guatemala. (2008). '], ['Decreto Número 57-2008: Ley de Acceso a la Información Pública', 1], ['. Secretaría contra la Violencia Sexual, Explotación y Trata de Personas. https://acceso.svet.gob.gt/wpsvet/wp-content/uploads/2026/02/DECRETO-57-2008-LEY-DE-ACCESO-A-LA-INFORMACION-PUBLICA.pdf']],
  [['Emisoras Unidas. (2026, 16 de julio). '], ['Comisión de Asuntos de Seguridad analiza Iniciativa de Ley de Protección de Datos Personales', 1], ['. https://emisorasunidas.com/nacional/2026/07/16/comision-de-asuntos-de-seguridad-analiza-iniciativa-de-ley-de-proteccion-de-datos-personales/']],
  [['Estrategia & Negocios. (2025, 17 de julio). '], ['Ranking de bancarización de los países de Centroamérica, según el informe Global Findex', 1], ['. https://www.revistaeyn.com/finanzas/ranking-de-bancarizacion-de-los-paises-de-centroamerica-segun-el-informe-global-findex-OG26642185']],
  [['Finnovista, Banco Interamericano de Desarrollo y BID Invest. (2024). '], ['Fintech en América Latina y el Caribe: Un ecosistema consolidado con potencial para aportar a la inclusión financiera regional', 1], [' (Monografía del BID n.º 1220). Banco Interamericano de Desarrollo. https://publications.iadb.org/publications/spanish/document/Fintech-en-America-Latina-y-el-Caribe-un-ecosistema-consolidado-con-potencial-para-aportar-a-la-inclusion-fianciera-regional.pdf']],
  [['Howard, M. y LeBlanc, D. (2003). '], ['Writing secure code', 1], [' (2.ª ed.). Microsoft Press.']],
  [['International Organization for Standardization e International Electrotechnical Commission. (2022a). '], ['Information security, cybersecurity and privacy protection — Information security management systems — Requirements', 1], [' (ISO/IEC 27001:2022). https://www.iso.org/standard/27001']],
  [['International Organization for Standardization e International Electrotechnical Commission. (2022b). '], ['Information security, cybersecurity and privacy protection — Guidance on managing information security risks', 1], [' (ISO/IEC 27005:2022). https://www.iso.org/standard/80585.html']],
  [['Joint Task Force Transformation Initiative. (2012). '], ['Guide for conducting risk assessments', 1], [' (NIST SP 800-30 Rev. 1). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-30r1']],
  [['Junta Monetaria. (2021). '], ['Resolución JM-104-2021: Reglamento para la Administración del Riesgo Tecnológico', 1], ['. Banco de Guatemala. https://banguat.gob.gt/sites/default/files/banguat/Publica/Res_JM/2021/Res_JM-104-2021.pdf']],
  [['National Institute of Standards and Technology. (2024). '], ['The NIST Cybersecurity Framework (CSF) 2.0', 1], [' (NIST CSWP 29). https://doi.org/10.6028/NIST.CSWP.29']],
  [['OWASP Foundation. (s. f.). '], ['OWASP Web Security Testing Guide (WSTG)', 1], ['. https://owasp.org/www-project-web-security-testing-guide/']],
  [['OWASP Foundation. (2023). '], ['OWASP API Security Top 10 2023', 1], ['. https://owasp.org/API-Security/editions/2023/en/0x11-t10/']],
  [['OWASP Foundation. (2024). '], ['OWASP Threat Dragon', 1], ['. https://owasp.org/www-project-threat-dragon/']],
  [['OWASP Foundation. (2025). '], ['OWASP Top 10:2025', 1], ['. https://owasp.org/Top10/2025/']],
  [['OWASP Mobile Application Security Project. (2024). '], ['OWASP Mobile Application Security Verification Standard (MASVS)', 1], [' (versión 2.1.0). https://mas.owasp.org/MASVS/']],
  [['PCI Security Standards Council. (2024). '], ['Payment Card Industry Data Security Standard', 1], [' (versión 4.0.1). https://www.pcisecuritystandards.org/']],
  [['Scarfone, K., Souppaya, M., Cody, A. y Orebaugh, A. (2008). '], ['Technical guide to information security testing and assessment', 1], [' (NIST SP 800-115). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-115']],
  [['Shostack, A. (2014). '], ['Threat modeling: Designing for security', 1], ['. Wiley.']],
];
const referencias = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('Referencias')] }),
  ...refs.map(parts => new Paragraph({
    indent: { left: 720, hanging: 720 },
    children: parts.map(([t, it]) => new TextRun({ text: t, italics: !!it })),
  })),
];

const mk = (children) => new Document({ creator: 'Grupo Q-Wallet', styles, sections: [{ properties: { page }, headers: { default: header }, children }] });

Promise.all([
  Packer.toBuffer(mk([...portada, ...resumen, ...indice])).then(b => fs.writeFileSync(OUT + '/Entrega1_Seccion_0_Portada_Resumen_Indice.docx', b)),
  Packer.toBuffer(mk(referencias)).then(b => fs.writeFileSync(OUT + '/Entrega1_Referencias.docx', b)),
]).then(() => console.log('ok', refs.length, 'referencias'));
