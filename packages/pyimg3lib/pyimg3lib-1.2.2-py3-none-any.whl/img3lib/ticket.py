
from .der import DER
from .utils import readPlist


def readApTicket(ticket):
    data = readPlist(ticket)
    return DER(data).parse()
