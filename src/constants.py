from rdflib import Namespace

EX = Namespace("http://prototype/data/")
TMR = Namespace("http://tmr#")

PRIORITY_RANK = {
    "urgent": 0,
    "asap": 1,
}

FALLBACK_RANK = 99