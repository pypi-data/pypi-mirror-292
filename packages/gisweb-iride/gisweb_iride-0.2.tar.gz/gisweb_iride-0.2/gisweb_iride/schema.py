from typing import Any
from pydantic import BaseModel, EmailStr
from enum import Enum

class IFlussoEnum(str, Enum):
    ENTRATA = "A"
    USCITA = "P"
    INTERNO = "I"

class IAzioneEnum(str, Enum):
    ESEGUI = "ESEGUI"
    CARICO = "CARICO"
    
class ISmistamentoEnum(str, Enum):
    CONOSCENZA = "CONOSCENZA"
    COMPETENZA = "COMPETENZA"

class IAmministrazione(BaseModel):
    Denominazione: str
    CodiceAOO: str
    CodiceEnte: str
    IndirizzoTelematico: EmailStr

class IConfigProtocollo(BaseModel):
    wsUrl: str
    wsUser: str
    wsEnte: str
    wsPassword: str
    amministrazione: IAmministrazione
    applicativo: str | None = None
    
class BaseRet(BaseModel):
    lngErrNumber: int = 0
    strErrString: str = ''

class ILoginRet(BaseRet):
    strDST: str | None
    
class IProtocolloResult(BaseRet):
    lngNumPG: int = 0
    lngAnnoPG: int = 0
    strDataPG: str = ''
    lngDocID: int = 0


class IAllegato(BaseModel):
    id: int | None = None
    descrizione: str
    tipo: str
    nome: str
    content: Any
    size: int
    mimetype: str
    ext: str

class IFascicolo(BaseModel):
    numero: str = ""
    anno:str = ""
    
class IParametro(BaseModel):
    nome: str
    valore: str

class ISoggettoProtocollo(BaseModel):

    Nome: str | None = None
    Cognome: str | None = None
    Denominazione: str | None = None
    CodiceFiscale: str
    IndirizzoTelematico: str
    TipoSoggetto: str | None = ""
    Principale: bool = True
    Titolo: str | None = ""
    
class IDataProtocollo(BaseModel):
    Soggetti: list[ISoggettoProtocollo] = []
    Flusso: str
    Oggetto: str
    Classifica: str
    UO: str
    Fascicolo: IFascicolo | None = None
    MittenteInterno: str = ""
    MezzoInvio: str = ""
    Parametri: list[IParametro] | None = []
    TipoDocumento: str = "GEN"
    NumeroRegistrazione: str = '0'
    DataRegistrazione: str = '0'
    LivelloRiservatezza: str = ""
    DataFineRiservatezza: str = ""   
    Principale: IAllegato | str = ""
    Allegati: list[IAllegato] = []
    
