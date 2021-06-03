# parkimise-registreerimine
Tegemist on veebitarkvaraga, kus on võimalik registreeritud kasutajal alustada ja lõpetada parkimine. Server-side kasutab Python Flaski ja MySQL andmebaase.
 ***
 Failisüsteem:
 * [küljendus]
    * lehekülgede päised ja jalused
 * [leheküljed]
    * erinevad veebilehe leheküljed, mis jäävad päise ja jaluse vahele
 * [veateated]
    * leheküljed, mida näidatakse, kui midagi läheb valesti (nt vale parool, lehekülge ei leita jms)
 * funktsioonid.py
    * veebilehtede töötlemiseks kasutatavad funktsioonid
 * main.py
    * põhifunktsioon
    * Flask serveri seadistamine
    * päringute töötlemine
    * tervete veebilehtede kuvamine
 * andmebaas.sql
    * andmebaasi eksport
 ***
 Näidiskasutajate sisselogimisinfo:
 > Administraator:  
 >U: `admin`\
 >P: `admin`
 >
 > Näidiskasutaja 1:  
 >U: `parkija1`\
 >P: `1234`
 >
 > Näidiskasutaja 2:  
 >U: `parkija2`\
 >P: `abc123` 