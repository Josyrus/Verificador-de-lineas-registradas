# -*- coding: utf-8 -*-
"""
Directorio de compañías telefónicas y sus portales de consulta de líneas
vinculadas, tomado de:
https://portal.crt.gob.mx/plataformas-de-consulta-de-las-companias-telefonicas

Cada entrada de CARRIERS: (nombre, url).

Muchas compañías son Operadores Móviles Virtuales que corren sobre la red
de Altán y comparten el mismo portal de consulta
("https://rnu.altanredes.com/consulta"). En vez de repetir esa fila ~90
veces, se agrupan en una sola entrada "Redes ALTÁN" y sus nombres
comerciales se guardan en PORTAL_ALIASES para que el buscador los siga
encontrando (ver buscar()).
"""

CARRIERS = [
    ("Redes ALTÁN", "https://rnu.altanredes.com/consulta"), #Provedor de varios provedores virutales
    ("Freedompop", "https://vinculatulinea.com/freedompop/my-lines"), # Provedor virtual de Telcel
    ("Abib", "https://abib.com.mx/#/consultatuslineas"),
    ("Abib/Internet del Bienestar", "https://www.abibinternetdelbienestar.mx/consultatulinea"),
    ("ALLCE", "https://vinculacion.allce.mx/consulta"),
    ("Alestra móvil", "https://vinculatulinea.alestra.mx/alestra-movil/vinculacion"),
    ("AT&T, Unefon y WIM marca digital AT&T", "https://att.com.mx/controlpersonal"),
    ("Beneleit Móvil", "https://beneleit.mx/consultalineas"),
    ("Bestel", "https://facturacion.bestel.com.mx"), #Revisar login
    ("BlackFon", "https://registro.blackfon.mx/consulta"),
    ("BuenoCell", "https://buenocell.mx/consultalineas"),
    ("Cablecom", "https://facturacion.bestel.com.mx"), #Revisar login
    ("Celsfi", "https://vinculacion.celfi.com.mx/consulta"), 
    ("Dalefon", "https://www.dalefon.mx/vinculatulinea"),
    ("Dalefon/Internet para el Bienestar", "https://www.internetbienestarmex.com/vinculatulinea"),
    ("Dialo", "https://dialo.mx/vinculatulinea/consulta.html"),
    ("Dua", "https://consulta.logisticaacn.mx"),
    ("Exis", "https://www.exis.mx/#/gestionatulinea"),
    ("Fedego!", "https://consulta.logisticaacn.mx"),
    ("Flash Mobile", "https://consulta.logisticaacn.mx"),
    ("Grupo Bitelit", "https://rnu.grupobitelit.com/mx/line-status"),
    ("IENTC", "https://vinculacion-consulta.ientc.net/"),
    ("Inxel", "https://inxel.mx/consulta-vinculacion"),
    ("Igou Telecom", "https://vinculacion.igou.mx/"),
    ("Infynit", "https://vinculate.infynit.mx/"),
    ("Izzi", "https://www.izzi.mx/login"),
    ("Jamachulel Móvil", "https://www.jamachulelmovil.com/consulta-vinculacion"),
    ("Link Móvil", "https://movil.linkteconectamos.com/consultar-vinculacion/"),
    ("Mega Móvil", "https://consultavinculacion.megamovil.mx"),
    ("Mi móvil", "https://vinculacion.mimovil.com.mx/consulta"),
    ("Mirlo", "https://mirlo.com/vincularlinea/consulta"),
    ("MoBig", "https://mobig.mx/vinculatulinea/consulta-curp"),
    ("MoBig/Internet para el bienestar", "https://femaseisa.com/vinculatulinea/consulta-curp"),
    ("Mosi", "https://vinculacion.mosi.mx/consulta"),
    ("Newww", "https://consultavinculacion.newww.mx"),
    ("Nextor Movil", "https://vinculacion.nextormovil.mx"),
    ("OUI", "https://vinculatulinea.com/oui/my-lines"), # Mismo dominio, diferente ruta
    ("Oxio", "https://verificar.oxiomobile.com/consultatuslineas"),
    ("Por Amor a Puebla Conecta", "https://www.poramorapueblaconecta.com/consulta-vinculacion"),
    ("Red Aguila", "https://consultavinculacion.redaguila.com.mx"),
    ("Red Potencia", "https://redpotencia.net/lineasvinculadas"),
    ("Red Potencia/Internet para el Bienestar", "https://internetbienestar.net/lineasvinculadas"),
    ("Redphone Koonol", "https://redphone.vinculacion.koonolmexico.com/consulta"),
    ("Redphone", "https://vinculacion.redphone.com.mx/consulta"),
    ("Sky", "https://micuenta.sky.com.mx"),
    ("Sorcel", "https://www.soriup.mx/consultavinculacion"),
    ("Telcel", "https://registro.telcel.com/vinculatulinea/#/"),
    ("Teléfonica Movistar", "https://www.movistar.com.mx/consulta-tu-linea"),
    ("Tokamóvil", "https://tokamovil.mx/cumplimiento/consulta-vinculacion"),
    ("Ubix", "https://www.ubix.mx/consulta-tu-linea/"),
    ("Viasat", "https://viasatprepago.com.mx/vinculatulinea/"),
    ("Viral Cel", "https://www.viralcel.com/mi-linea"),
    ("Virgin Mobile", "https://virginmobile.mx/v1/consultatulinea"),
    ("Weex", "https://weex.mx/consultalineas.html"),
    ("Wiicel", "https://wiicel.com"),
    ("Yo mobile", "https://mx.yomobile.com/consulta"),
    ("Yobi Telecom", "https://vinculatulinea.com/yobitelecom/my-lines"), # Mismo dominio, diferente ruta
    ("Yu Movil", "https://www.yumovil.com.mx/login") #otro jodido login
]

# Nombres comerciales que corren sobre la red de Altán y por lo tanto usan
# el portal "Redes ALTÁN" de arriba. Se buscan por nombre pero resuelven a
# esa fila — ver buscar().
PORTAL_ALIASES = {
    "2y2x": "Redes ALTÁN",
    "Abafon": "Redes ALTÁN",
    "Abix": "Redes ALTÁN",
    "Addinteli": "Redes ALTÁN",
    "AI Telecomm": "Redes ALTÁN",
    "Appcel": "Redes ALTÁN",
    "Axios Mobile": "Redes ALTÁN",
    "Bait": "Redes ALTÁN",
    "BienCel": "Redes ALTÁN",
    "Bigcel": "Redes ALTÁN",
    "Bromovil": "Redes ALTÁN",
    "Bnext": "Redes ALTÁN",
    "CFE": "Redes ALTÁN",
    "Chip Macropay": "Redes ALTÁN",
    "CoolMobile": "Redes ALTÁN",
    "Comunicaciones Green": "Redes ALTÁN",
    "Conect2": "Redes ALTÁN",
    "Conectacel México": "Redes ALTÁN",
    "Chuliphone": "Redes ALTÁN",
    "Diri Móvil": "Redes ALTÁN",
    "Diré Movil": "Redes ALTÁN",
    "ENI Networks": "Redes ALTÁN",
    "Fangio Mobile": "Redes ALTÁN",
    "Fibracell": "Redes ALTÁN",
    "FRC Mobile": "Redes ALTÁN",
    "Gamers": "Redes ALTÁN",
    "Gane": "Redes ALTÁN",
    "Glovo Telecom": "Redes ALTÁN",
    "Gmovil": "Redes ALTÁN",
    "Grupo Inten": "Redes ALTÁN",
    "Hashtag": "Redes ALTÁN",
    "Hicel": "Redes ALTÁN",
    "I AM Abundance": "Redes ALTÁN",
    "Interlinked": "Redes ALTÁN",
    "Inxel/Internet para el Bienestar": "Redes ALTÁN",
    "Iusatel": "Redes ALTÁN",
    "Inphonity": "Redes ALTÁN",
    "IPB Conec-Rural": "Redes ALTÁN",
    "JRmovil": "Redes ALTÁN",
    "JRmovil/Internet para el Bienestar": "Redes ALTÁN",
    "Kolors Mobile": "Redes ALTÁN",
    "Likephone": "Redes ALTÁN",
    "Maya Móvil": "Redes ALTÁN",
    "Maifon": "Redes ALTÁN",
    "México Móvil": "Redes ALTÁN",
    "Mexfon": "Redes ALTÁN",
    "Mi móvil/Altán": "Redes ALTÁN",
    "MobileArionet": "Redes ALTÁN",
    "Movired": "Redes ALTÁN",
    "Móvil para Todos": "Redes ALTÁN",
    "Miio": "Redes ALTÁN",
    "Mujer Móvil": "Redes ALTÁN",
    "Nabi": "Redes ALTÁN",
    "Netmas": "Redes ALTÁN",
    "Netwey": "Redes ALTÁN",
    "Ocean Móvil": "Redes ALTÁN",
    "On-Link": "Redes ALTÁN",
    "Orange": "Redes ALTÁN",
    "OUI/Altán": "Redes ALTÁN",
    "Othisi Mobile": "Redes ALTÁN",
    "Pagacel": "Redes ALTÁN",
    "PilloFon": "Redes ALTÁN",
    "Playcell": "Redes ALTÁN",
    "Red Blak": "Redes ALTÁN",
    "Red Dog": "Redes ALTÁN",
    "Redicoppel": "Redes ALTÁN",
    "Redy Movil": "Redes ALTÁN",
    "Retemex": "Redes ALTÁN",
    "RETESEC": "Redes ALTÁN",
    "Rex Movil": "Redes ALTÁN",
    "Rincel": "Redes ALTÁN",
    "Secure Witness": "Redes ALTÁN",
    "Sfon": "Redes ALTÁN",
    "Sueñainc": "Redes ALTÁN",
    "Spot 1": "Redes ALTÁN",
    "Softcell": "Redes ALTÁN",
    "Starline": "Redes ALTÁN",
    "Telefónica Luna": "Redes ALTÁN",
    "Telgen": "Redes ALTÁN",
    "Telmovil": "Redes ALTÁN",
    "Teracel": "Redes ALTÁN",
    "TIC-OMV": "Redes ALTÁN",
    "Tuis": "Redes ALTÁN",
    "TurboCel": "Redes ALTÁN",
    "Turbored": "Redes ALTÁN",
    "Ultracel": "Redes ALTÁN",
    "Valor Telecomm": "Redes ALTÁN",
    "Vasanta": "Redes ALTÁN",
    "VivaMX": "Redes ALTÁN",
    "Wiki Katat": "Redes ALTÁN",
    "Wimotelecom": "Redes ALTÁN",
    #freedompop aliases
    "AhorroCel":"Freedompop",
    "Chedraui Móvil":"Freedompop",
    "OXXO CEL": "Freedompop",
    "Uber Cel": "Freedompop",
    "":"Internet Bienestar",
}



_CARRIERS_BY_NAME = {nombre: url for nombre, url in CARRIERS}


def _normalizar(texto: str) -> str:
    """minúsculas y sin acentos, para que 'altan' encuentre 'ALTÁN'."""
    import unicodedata
    sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sin_acentos.lower()


def buscar(texto: str):
    """Busca `texto` entre los nombres de CARRIERS y entre PORTAL_ALIASES.

    Regresa una lista de tuplas (nombre_a_mostrar, url, alias_de) donde
    alias_de es None si el match fue directo, o el nombre comercial que
    escribió el usuario si el match vino de un alias de Altán (para poder
    avisarle "Bnext se revisa en Redes ALTÁN").
    """
    texto = _normalizar((texto or "").strip())
    if not texto:
        return [(nombre, url, None) for nombre, url in CARRIERS]

    resultados = []
    vistos = set()

    for nombre, url in CARRIERS:
        if texto in _normalizar(nombre):
            resultados.append((nombre, url, None))
            vistos.add(nombre)

    for alias, nombre_real in PORTAL_ALIASES.items():
        if texto in _normalizar(alias) and nombre_real not in vistos:
            resultados.append((nombre_real, _CARRIERS_BY_NAME[nombre_real], alias))
            vistos.add(nombre_real)

    return resultados
