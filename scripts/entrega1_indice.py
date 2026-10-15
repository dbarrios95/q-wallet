"""Actualiza los números de página del índice (campo TOC) del Word ensamblado.

Uso: python scripts/entrega1_indice.py docs/entregas/Entrega1_Informe_QWallet.docx
Renderiza el Word con LibreOffice (soffice), busca la página de cada título y
reescribe el número en las entradas TOC1-TOC3. El campo sigue siendo un TOC de
Word: en Word basta con clic derecho -> Actualizar campo si cambia la paginación.
Requiere: LibreOffice (soffice) y pdftotext (Poppler).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

DOCX = sys.argv[1]
SOFFICE = os.environ.get('SOFFICE', 'soffice')


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def pages_text(docx):
    tmp = tempfile.mkdtemp()
    subprocess.run([SOFFICE, '--headless', '--convert-to', 'pdf', '--outdir', tmp, docx],
                   check=True, capture_output=True)
    pdf = os.path.join(tmp, os.path.splitext(os.path.basename(docx))[0] + '.pdf')
    out = subprocess.run(['pdftotext', '-layout', pdf, '-'], check=True, capture_output=True, text=True).stdout
    shutil.rmtree(tmp)
    return out.split('\f')


def main():
    z = zipfile.ZipFile(DOCX)
    x = z.read('word/document.xml').decode('utf-8')
    entry = re.compile(r'(<w:p><w:pPr><w:pStyle w:val="TOC[123]"/>(?:(?!</w:pPr>).)*</w:pPr>.*?<w:t xml:space="preserve">)([^<]*)'
                       r'(</w:t></w:r><w:r><w:t xml:space="preserve">\t)(\d+)(</w:t></w:r>)', re.S)
    pages = [[norm(l) for l in p.splitlines()] for p in pages_text(DOCX)]
    toc_page = next(i for i, p in enumerate(pages) if 'Índice' in p)
    pos = 0
    found = []
    for m in entry.finditer(x):
        title = norm(m.group(2))
        for i in range(pos, len(pages)):
            if i == toc_page:
                continue
            if any(l == title or l.startswith(title + ' ') and len(l) < len(title) + 3 for l in pages[i]):
                found.append((m, i + 1))
                pos = i
                break
        else:
            raise SystemExit(f'No se encontró el título: {title}')
    for m, pg in reversed(found):
        x = x[:m.start(4)] + str(pg) + x[m.end(4):]
    tmp = DOCX + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for it in z.infolist():
            zo.writestr(it, x.encode('utf-8') if it.filename == 'word/document.xml' else z.read(it.filename))
    shutil.move(tmp, DOCX)
    for m, pg in found:
        print(f'{norm(m.group(2))} -> {pg}')


if __name__ == '__main__':
    main()
