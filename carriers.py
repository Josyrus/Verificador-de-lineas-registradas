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
    ("Bestel", "https://facturacion.bestel.com.mx"), #Revisar login PD:2 no tengo idea que tenga que ver con Cablecom y tampoco las ganas de descubrirlo
    ("Abib", "https://abib.com.mx/#/consultatuslineas"),
    ("ALLCE", "https://vinculacion.allce.mx/consulta"),
    ("Alestra móvil", "https://vinculatulinea.alestra.mx/alestra-movil/vinculacion"),
    ("AT&T, Unefon y WIM marca digital AT&T", "https://att.com.mx/controlpersonal"),
    ("Beneleit Móvil", "https://beneleit.mx/consultalineas"),
    ("BlackFon", "https://registro.blackfon.mx/consulta"),
    ("BuenoCell", "https://buenocell.mx/consultalineas"),
    ("Celsfi", "https://vinculacion.celfi.com.mx/consulta"), 
    ("Dalefon", "https://www.dalefon.mx/vinculatulinea/"),
    ("Dalefon/Internet para el Bienestar", "https://www.internetbienestarmex.com/vinculatulinea"),
    ("Diri Móvil", "https://vinculacion.diri.mx/consulta-vinculacion/"),
    ("Dialo", "https://dialo.mx/vinculatulinea/consulta.html"),
    ("Dua", "https://vinculacion.dua.mx/consulta-vinculacion/"),
    ("Exis", "https://www.exis.mx/vinculatulinea"),
    ("Fedego!", "https://vinculacion.fedego.mx/consulta-vinculacion/"),
    ("Flash Mobile", "https://vinculacion.miflash.mx/consulta-vinculacion/"),
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
    ("Mirlo", "https://mirlo.com/vinculatulinea/consulta"),
    ("MoBig", "https://mobig.mx/vinculatulinea/consulta-curp"),
    ("MoBig/Internet para el bienestar", "https://femaseisa.com/vinculatulinea/consulta-curp"),
    ("Mosi", "https://vinculacion.mosi.mx/consulta"),
    ("Movistar", "https://www.movistar.com.mx/consulta-tu-linea"),
    ("Newww", "https://consultavinculacion.newww.mx"),
    ("Nextor Movil", "https://vinculacion.nextormovil.mx/consulta-vinculaciones"),
    ("OUI", "https://vinculatulinea.com/oui/my-lines"), # Mismo dominio, diferente ruta
    ("Oxio", "https://verificar.oxiomobile.com/consultatuslineas"),
    ("Pillofon", "https://vinculacion.pillofon.mx/consulta-vinculacion/"),
    ("Por Amor a Puebla Conecta", "https://www.poramorapueblaconecta.com/consulta-vinculacion"),
    ("Red Aguila", "https://consultavinculacion.redaguila.com.mx"),
    ("Redphone", "https://vinculacion.redphone.com.mx/consulta"),
    ("Sky", "https://micuenta.sky.com.mx"), #requiere login
    ("Sorcel", "https://www.soriup.mx/consultavinculacion"),
    ("Telcel", "https://registro.telcel.com/vinculatulinea/#/"),
    ("Tokamóvil", "https://tokamovil.mx/cumplimiento/consulta-vinculacion"),
    ("Ubix", "https://www.ubix.mx/consulta-tu-linea/"),
    ("Viasat", "https://viasatprepago.com.mx/vinculatulinea/"),
    ("Viral Cel", "https://www.viralcel.com/mi-linea"), #requiere
    ("Virgin Mobile", "https://virginmobile.mx/v1/consultatulinea"),
    ("Weex", "https://weex.mx/consultalineas.html"),
    ("Yo mobile", "https://mx.yomobile.com/consulta"),
    ("Yobi Telecom", "https://vinculatulinea.com/yobitelecom/my-lines"), # Mismo dominio, diferente ruta
    ("Yu Movil", "https://www.yumovil.com.mx/login") #otro jodido login
]

# Nombres comerciales que corren sobre otras redes telcel, altan, diri
PORTAL_ALIASES = {
    "2y2x": "Redes ALTÁN",
    "Abafon": "Redes ALTÁN",
    "Abix": "Redes ALTÁN",
    "Abib/Internet del Bienestar":"Redes ALTÁN",
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
    "Playcell": "Redes ALTÁN",
    "Red Blak": "Redes ALTÁN",
    "Red Dog": "Redes ALTÁN",
    "Red Potencia": "Redes ALTÁN",
    "Red Potencia/Internet para el Bienestar":"Redes ALTÁN",
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
    "Wiicel":"Redes ALTÁN",
    #freedompop aliases
    "AhorroCel":"Freedompop",
    "Chedraui Móvil":"Freedompop",
    "OXXO CEL": "Freedompop",
    "Uber Cel": "Freedompop",
    #bestel alias
    "BuenoCell": "Bestel"
}



_CARRIERS_BY_NAME = {name: url for name, url in CARRIERS}


def _normalize_text(text: str) -> str:
    """minúsculas y sin acentos, para que 'altan' encuentre 'una linea'."""
    import unicodedata
    normalized_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return normalized_text.lower()


def search_carriers(text: str):
    """Busca `texto` entre los nombres de CARRIERS y entre PORTAL_ALIASES.
    Regresa una lista de tuplas (nombre_a_mostrar, url, alias_de) donde
    alias_de es None si el match fue directo, o el nombre comercial que
    escribió el usuario si el match vino de un alias.
    """
    text = _normalize_text((text or "").strip())
    if not text:
        return [(name, url, None) for name, url in CARRIERS]

    results = []
    vistos = set()

    for name, url in CARRIERS:
        if text in _normalize_text(name):
            results.append((name, url, None))
            vistos.add(name)

    for alias, nombre_real in PORTAL_ALIASES.items():
        if text in _normalize_text(alias) and nombre_real not in vistos:
            results.append((nombre_real, _CARRIERS_BY_NAME[nombre_real], alias))
            vistos.add(nombre_real)

    return results
