1. Mitä tekoäly teki hyvin?

Ensinnäkin tekoäly tuotti heti ajettavan ohjelman, mikä oli hyvä, sillä sitä pääsi heti testaamaan. Tekoäly myös toteutti pyytämäni alustavat vaatimukset hyvin, jonka jälkeen projektin edetessä myös auttoi osassa lisätotetuksista mallikkaasti.

Erityisesti esim. ohjelman jako eri tiedostoihin, päällekkäisten varauksien estäminen, koodin suoraan ajettavaksi luonti, testidatan luonti sekä pyytämäni web-applikaation luominen onnistui hyvin.

2. Mitä tekoäly teki huonosti?

Tekoäly jätti aluksi mm. salasanatarkastelun kokonaan pois ja päällekkäisten kirjotuksien tarkastaminen oli aluksi huonosti skaalautuva. Myöskään pyytämäni web-applikaatio toteutus ei ollut aluksi kovin käyttäjäystävällinen, joten sitä sai jatkokehittää melko paljon.

3. Mitkä olivat tärkeimmät parannukset, jotka teit tekoälyn tuottamaan koodiin ja miksi?

Minun mielestä tärkeimmät parannukset olivat:
    1. Rinnakkaisuuden hallinta
        - Estettiin ns. "race condition" tilanteet varauslogiikassa lisäämällä threading.Lock
        - Teoreettisen samanaikaisen varauksen estäminen

    2. Olio-ohjelmoinnin lisääminen
        - Sanakirjojen tilalle luokat
        - Teki koodista selkeämpää ja on muutenkin yleisten toimintatapojen mukaista verrattuna alkuperäiseen ratkaisuun

    3. API:n suorituskyvyn parantaminen lukemalla start ja end parametrit
        - Suodattaa palautettavat varaukset vain tämänhetkisenä näkyvälle kalenterinäkymälle, joka tehostaa toimintaa kun varaushistoriaa kasvaa merkittävästi

    4. Tietoturvan parantaminen salasanojen lisäyksellä
        - Salasanatoiminallisuus lisää parantaa ohjelman tietoturvaa
        - Tosin esim. Admin salasana on oletuksena kaikille nähtävissä, mutta salasanojen lisäys oli enemmänkin näköisoperaatio, jonka tarkoituksena oli osoittaa, että oikeaan ohjelmaan olisi äärimmäisen tärkeää lisätä salasanat käyttäjille

    5. Liiallisten varausten, ts. spämmin, estäminen käyttäjiltä
        - Tehostaa ohjelman toiminnalisuutta

    6. Web-applikaation käyttäjäkokemuksen parantaminen

    