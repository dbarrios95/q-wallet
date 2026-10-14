import zipfile,sys,re,shutil
src=sys.argv[1]; tmp=src+'.tmp'
zin=zipfile.ZipFile(src); x=zin.read('word/document.xml').decode()
marks=re.findall(r'@@TOC(\d+)@@',x); first,last=marks[0],marks[-1]
i=x.index(f'@@TOC{first}@@'); rs=max(x.rfind('<w:r>',0,i),x.rfind('<w:r ',0,i))
begin=('<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
       '<w:r><w:fldChar w:fldCharType="separate"/></w:r>')
x=x[:rs]+begin+x[rs:]
j=x.index(f'@@TOC{last}@@'); pe=x.index('</w:p>',j)
x=x[:pe]+'<w:r><w:fldChar w:fldCharType="end"/></w:r>'+x[pe:]
x=re.sub(r'@@TOC\d+@@','',x)
zout=zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    zout.writestr(it, x.encode() if it.filename=='word/document.xml' else zin.read(it.filename))
zout.close(); shutil.move(tmp,src); print('toc field ok', len(marks))
