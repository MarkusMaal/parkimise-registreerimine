from main import session


def Ava_Dokument(failinimi):
    f = open(failinimi, "r", encoding="UTF-8")
    out = f.read()
    f.close()
    return out


def TöötleParkimiseLehte(numbrimärk, alustatud, nimi):
    leht = Ava_Leht("leheküljed/uus_parkimine.html")
    leht = leht.replace("{0}", AntiXSS(session["username"]))
    leht = leht.replace("{1}", numbrimärk)
    leht = leht.replace("{3}", AntiXSS(nimi))
    if alustatud:
        leht = leht.replace("{2}", " disabled")
    else:
        leht = leht.replace("{2}", "")
    return leht


def AntiXSS(sõne):
    sõne = sõne.replace("<", "&lt;")
    sõne = sõne.replace(">", "&gt;")
    return sõne.replace("\"", "&quot;")


def Ava_Leht(lehenimi):
    return Ava_Dokument("küljendus/päis.html") + Ava_Dokument(lehenimi) + Ava_Dokument("küljendus/jalus.html")


def kontrolli_sobivust(number):
    if not len(number) == 6:
        return False
    else:
        tähestik = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(3):
            sobiv = False
            for n in range(10):
                if number[i] == str(n):
                    sobiv = True
            if not sobiv:
                return False
            sobiv = False
            for täht in tähestik:
                if number[i+3] == täht:
                    sobiv = True
            if not sobiv:
                return False
        return True
