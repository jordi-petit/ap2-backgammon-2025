# Primera Pràctica d'AP2: Backgammon

En aquesta pràctica, tindràs l'oportunitat de desenvolupar el nucli d'un servidor de Backgammon.

Caldrà que implementis la lògica del joc, programis un bot que jugui contra humans o altres bots, gestionis jugadors i partides... Ara bé, no has de considerar la interfície d'usuari ni la interacció amb la xarxa.

## El joc del Backgammon

El backgammon és un joc de tauler per a dos jugadors que combina estratègia i atzar. És un dels jocs més antics del món, amb orígens que es remunten a milers d'anys enrere.

![Backgammon](images/bg.png 'Backgammon')

Cada jugador té 15 fitxes que mou en direccions contràries segons el resultat de dos daus, seguint un recorregut a través de 24 punts del tauler. L'objectiu és treure totes les fitxes abans que l'oponent, tot frenant-lo bloquejant o capturant-ne fitxes solitàries.

Pots trobar el detall de les regles del backgammon a https://www.bkgm.com/rules.html i és convenient que les tinguis ben clares. Pots instal·lar un joc de backgammon al teu mòbil o jugar en línia per practicar.

Per simplificar, en aquesta pràctica no considerarem la "doblada" (el dau doblador amb valors 2, 4, 8, 16, 32, 64) ni els diferents tipus de victòria (normal, gammon o backgammon).

## Objectius

L'objectiu de la pràctica és que implementis el nucli d'un servidor de backgammon que permeti gestionar partides entre usuaris registrats al sistema. El servidor en sí no s'ha d'implementar, aquesta responsabilitat no és teva. Per aconseguir aquest objectiu has de seguir aquests passos:

1. Implementar la lògica del joc del backgammon en una classe `Board` i d'altres associades que permeti aplicar moviments legals (i discernir els il·legals) a un tauler donat.

2. Sobre la classe `Board`, implementar un programa que permeti jugar una partida entre dos jugadors humans per la consola.

3. També sobre la classe `Board`, implementar una funció `bot` que, donat un tauler, retorni el millor moviment possible per al jugador que li toca moure segons una funció que avalua la qualitat dels taulers. Això també permetrà realitzar partides per la consola entre un jugador humà i un bot o entre dos bots.

4. Implementar una classe `User` que permeti enmagatzemar el perfil dels usuaris que es registren al servidor i una classe `Game` que permeti disputar i recuperar una partida entre dos usuaris. A més, implementar una classe `Arena` que ofereixi les principals funcionalitats del servidor: registrar i desregistrar usuaris, entrar i sortir de l'aplicació, crear, jugar i recuperar partides, mantenir la classificació de usuaris, etc.

Cadascun d'aquests passos es construeix sobre els anteriors.

Per a totes aquestes classes i funcions, has de proporcionar una interfície clara, senzilla i ben especificada. Igualment, has de donar una implementació correcta, cuidada, ben comentada i has de cobrir el teu codi amb tests unitaris. Com que en el futur el projecte es farà més gran, has de tenir cura de mantenir una bona organització del codi, i mantenir la independència entre la interfície i la implementació de les classes.

No es vol que implementis cap mena d'interfície d'usuari ni comunicació en xarxa, només la interacció per la consola. Tanmateix, per ajudar-te, ja tens fetes dues accions que dibuixen agradablement el tauler de joc.

## Pas 1. Mòdul `board.py`: el tauler de joc

El mòdul `board.py` ha de contenir la classe `Board` que representa l'estat actual d'una partida de Backgammon i implementa la lògica del joc. Aquest mòdul també ofereix alguns tipus addicionals senzills que ja es donen implementats i que es detallen a continuació.

### El tipus `Dice`

El tipus `Dice` serveix per representar el valor de dos daus.

![daus](images/daus.png 'daus')

Aquesta és la seva implementació:

```python
@dataclass
class Dice:
    die1: int  # 1..6
    die2: int  # 1..6

    def copy(self) -> Dice:
        return Dice(self.die1, self.die2)

    def is_double(self) -> bool:
        return self.die1 == self.die2

    def is_valid(self) -> bool:
        return 1 <= self.die1 <= 6 and 1 <= self.die2 <= 6
```

### El tipus `DiceCup`

El tipus `DiceCup` representa el gobelet on es barrejen els daus.

![gobelet](images/gobelet.png 'gobelet')

Aquesta és la seva implementació:

```python
class DiceCup:

    _a = 1664525
    _c = 1013904223
    _m = 2**32
    _seed: int

    def __init__(self, seed: int):
        self._seed = seed

    def roll(self) -> Dice:
        return Dice(self._next() % 6 + 1, self._next() % 6 + 1)

    def _next(self) -> int:
        self._seed = (self._a * self._seed + self._c) % self._m
        return self._seed
```

La idea és que un gobelet es crea amb una llavor (`seed`) i es pot anar cridant `roll` per obtenir la següent tirada dels daus. La implementació d'aquesta classe usa un generador `ranqd1` de nombres pseudoaleatoris congruencial lineal; pots veure-ho a https://en.wikipedia.org/wiki/Linear_congruential_generator.

El fet de tenir un gobelet vinculat a un joc permetrà que els tests unitaris siguin deterministes, ja que podràs controlar quins valors de daus es generen en cada partida. A més el disseny de tot el sistema ha d'assegurar que els jugadors no puguin conèixer el gobelet ni la seva llavor per tal de fer trampes predint els seus propers valors. En canvi, al final de la partida, els jugadors han de poder comprovar que els valors de daus generats s'han generat a partir de la llavor inicial. Això eliminarà qualsevol suspicàcia de trampa per part del sistema (és evident que els servidors d'Internet afavoreixen als jugador que paguen!).

### El tipus `Jump`

El tipus `Jump` serveix per representar el salt d'_una_ fitxa.

```python
@dataclass
class Jump:
    point: int  # 0..23 | -1 (bar)
    pips: int  # 1..6
```

Un salt indica quina fitxa es mou i quantes posicions avança. El valor de la posició de la fitxa (`point`) pot ser un enter de 0 a 23 per indicar una casella o un -1 per indicar la barra. El valor de les posicions que avança (`pips`) pot ser un enter de 1 a 6 i es correspon amb algun dels daus. Els valors que porten una peça més enllà de la posició 23 o abans de la 0 són vàlids i es consideren com a fitxes que cal treure (_bear off_).

### El tipus `Move`

El tipus `Move` serveix per representar la tirada d'un jugador durant el seu torn i és una seqüència de salts d'_algunes_ de les seves fitxes. Habitualment la llista tindrà llargada 2 però, en raó als daus dobles o als bloquejos, pot tenir llargada entre 0 i 4. Si un jugador no pot tirar, el moviment és una llista buida. Per senzillesa, suposarem que els jugadors no es poden rendir.

```python

@dataclass
class Move:
    jumps: list[Jump]  # length 0-4
```

### Constants i tipus per a jugadors

Hi ha dos jugadors: el `0` (blanc) i l'`1` (negre). Aquests valors es representen per les constants `WHITE` i `BLACK` (independentment de com es visualitzin després). La posició de la barra es representa per la constant `BAR`:

```python
WHITE = 0
BLACK = 1
BAR = -1
```

El tipus `Player` només permet enmagatzemar els valors `WHITE` i `BLACK`, el tipus `OptionalPlayer` permet enmagatzemar també `None`:

```python
type Player = Literal[0] | Literal[1]
type OptionalPlayer = Player | None
```

### El tipus `Board`

El tipus `Board` representa l'estat d'una partida de Backgammon i permet aplicar moviments a un tauler donat per obtenir-ne un de nou. El tauler inclou informació sobre les fitxes de cada jugador, les fitxes a la barra, les fitxes fora del tauler, el torn actual, quin jugador ha guanyat, els daus...
Es considera que el jugador blanc sempre comença la partida.

Les caselles del tauler es poden veure com una llista de 24 enters, on cada enter pot ser:

- 0: cap fitxa
- un valor estrictament positiu `n`: `n` fitxes blanques
- un valor estrictament negatiu `n`: `-n` fitxes negres

El jugador blanc avança de 0 cap a 23, i el jugador negre avança de 23 cap a 0. La casa del jugador blanc són doncs les caselles 18 a 23 i la del jugador negre les caselles 0 a 5. Quan blanc mou a "caselles" més grans que 23 és que treu fitxes i quan negre mou a "caselles" més petites que 0 és que també treu fitxes.

La classe `Board` ha de tenir aquesta interfície:

```python
class Board:
    def __init__(self, dice: Dice, turn: int=1, cells: list[int]|None=None, barW: int=0, barB: int=0) -> None: ...
    def copy(self) -> Board: ...
    def flip(self) -> Board: ...
    def cells(self) -> list[int]: ...
    def cell(self, i: int) -> int: ...
    def bar(self, player: Player) -> int: ...
    def off(self, player: Player) -> int: ...
    def dice(self) -> Dice: ...
    def turn(self) -> int: ...
    def current(self) -> OptionalPlayer: ...
    def winner(self) -> OptionalPlayer: ...
    def over(self) -> bool: ...
    def valid_moves(self) -> list[Move]: ...
    def is_valid_move(self, move: Move) -> bool: ...
    def play(self, move: Move) -> Board: ...
    def next(self, dice: Dice) -> Board: ...
```

La majoria d'aquestes operacions tenen un propòsit prou evident pel seu nom. Encarregeu-vos d'especificar-les totes adientment. Aquestes es mereixen una mica més d'explicació:

- El constructor "normal" només requereix un paràmetre: `dice`. La resta de paràmetres només són per ajudar a desenvolupar el programa i poder crear taulers específics, pels jocs de proves per exemple.

- La funció `flip` retorna un tauler amb els colors i sentits invertits. Aquest operació és útil per no haver de considerar continuament qui tira i en quin sentit: Enlloc de duplicar codi per blanc i per negre, fes-lo només per blanc i, si és negre, inverteix el tauler, treballa amb blanc i inverteix de nou el tauler resultant.

- La funció `play` retorna el tauler resultant d'aplicar un moviment al tauler actual. És una funció que no ha de modificar el tauler original. En el tauler resultant, els daus i el jugador actual encara són els que s'han jugat.

- És justament la funció `next` qui retorna un tauler amb els daus i jugador següents preparats pel proper torn. La secció següent mostra un codi que aclareix el rol de `play` i `next`.

Tots els mètodes han de verificar que els paràmetres siguin correctes i que no es violin les regles del backgammon. En cas contrari, han de llençar una excepció amb un missatge adequat. A tota la pràctica, si la invocació d'un mètode públic sobre un objecte provoca una excepció, el valor de l'objecte no ha de canviar, és com si no s'hagués fet res.

Per seguratat, si algun mètode retorna valors mutables, cal retornar una còpia dels valors originals per evitar que l'usuari pugui modificar-los directament. Per exemple, si un mètode retorna una llista, cal retornar una còpia de la llista original.

El mòdul `show.py` que subministrem conté una acció `show(board: Board)` que escriu un tauler pel terminal i una acció `draw(board: Board, filename: str)` que dibuixa un tauler de forma agradable en un fitxer PNG. Aquestes funcions et poden ser útils per depurar el teu codi o jugar al Backgammon, tal com faràs al pas següent. Aquí tens un exemple de com queda un `show` d'un tauler acabat de construir i daus 1-3:

![terminal](images/show.png 'terminal')

I aquí ho tens amb `draw`:

![Inicial](images/draw.png 'Inicial')

A les vistes, les caselles es numeren de 1 a 24 en el sentit del jugador actual per facilitar la seva identificació per part dels humans. En canvi, a la representació interna, les caselles es numeren de 0 a 23 en el sentit del jugador blanc.

## Pas 2: Mòdul `human_vs_human`: juguem!

El mòdul `human_vs_human.py` ha de contenir un senzill programa que permeti jugar una partida de Backgammon entre dos jugadors humans per la consola. Aquí en teniu un esbós:

```python
def main() -> None:
    seed = 123456
    cup = DiceCup(seed)
    board = Board(cup.roll())
    show(board)
    while not board.over():
        print("White move?")
        move = read_move()
        board = board.play(move)
        board = board.next(cup.roll())
        show(board)
        if not board.over():
            print("Black move?")
            move = read_move()
            board = board.play(move)
            board = board.next(cup.roll())
            show(board)
    print(f"Winner: {'W' if board.winner() == WHITE else 'B'}")
    print(f"Seed: {seed}")
```

## Pas 3: Mòdul `bot.py`: el bot (que vendrem com una IA perquè estan de moda)

El mòdul `bot.py` ha de contenir una funció `bot(board: Board) -> Move` que, donat un tauler, retorni el "millor" moviment possible per al jugador que li toca moure. Aquesta funció ha de semblar prou intel·ligent per jugar bé al Backgammon, però no ha de ser invencible. La funció `bot` ha de ser prou ràpida per generar un moviment en un temps imperceptible per a un humà.

La funció ha de ser determinista, és a dir, donat un tauler, ha de retornar sempre el mateix moviment.

Per implementar-la, fés una funció addicional que, donat un tauler, li assigni una puntuació. La funció `bot` ha de generar tots els moviments legals a partir del tauler donat i triar el moviment que maximitzi la puntuació del tauler resultant. Només cal considerar com queda el tauler després d'un moviment (a AP3 veuràs com fer-ho més intel·ligent considerant diferents nivells de profunditat).

Els elements que poden contribuir a la puntuació són:

- La distància de les fitxes fins a casa.
- El nombre de fitxes a la barra.
- El nombre de fitxes fora.
- La presència de fitxes solitàries.
- La possibilitat de fer una muralla més o menys llarga.
- Ètcetera.

Fés quelcom raonable però no hi dediquis massa temps.

Escriu també un programa `human_vs_bot.py` que permeti jugar una partida entre un jugador humà i un bot. Així podràs provar la vostra IA contra tu mateix o contra els teus familiars que fliparan de com de bona ets programant. Igualment, escriu un programa `bot_vs_bot.py` que permeti jugar una partida entre dos bots. Evidentment, pots fer jugar partides del teu bot contra bots dels teus companys, però no aprofitis l'ocasió per copiar.

Fixa't que no hi ha cap competició: L'avaluació d'aquesta part tindrà en compte la qualitat de la implementació de la teva IA, no els seus resultats comparats als dels companys.

## 4. Mòdul `arena.py`: Molta gent

El mòdul `arena.py` serà la base del servidor de Backgammon i és, en gran mesura, independent del joc en si. Per aquest mòdul has de definir les classes que s'esmenten a continuació, però la definició de la seva interfície ja no ve imposada i és responsabilitat teva.

Comença el mòdul `arena` per les classes `User` i `Game`:

- La classe `User` ha de mantenir la informació d'un usuari del sistema (un jugador), incloent (com a mínim) un identificador únic, el seu nom, el nombre de partides guanyades i el nombre de partides jugades.

- La classe `Game` ha de mantenir la informació d'una partida, incloent un identificador únic, els dos usuaris que l'han dut a terme, el tauler actual i la llista de moviments realitzats fins al moment. També ha d'oferir operacions per aplicar un moviment a la partida.

Després, completa el mòdul `arena` amb la classe `Arena` que permeti gestionar els usuaris i les seves partides. La classe `Arena` ha de donar suport en aquestes operacions:

- Registrar un nou usuari, tot donant-li un identificador únic.

- Donar de baixa un usuari, tot eliminant-lo de la llista d'usuaris.

- Entrar (connectar-se, fer _login_) a l'aplicació.

- Sortir (desconnectar-se, fer _logout_) de l'aplicació.

- Obtenir una llista de tots els usuaris registrats.

- Obtenir una llista de tots els usuaris connectats.

- Buscar un usuari pel sis indentificador.

- Buscar usuaris per nom.

- Crear una nova partida entre dos usuaris.

- Permetre als usuaris realitzar una partida.

- Obtenir la llista de totes les partides d'un usuari.

- Obtenir una partida en particular d'un usuari. Si és acabada, també cal retornar
  la llavor del gobelet.
- Obtenir la classificació dels usuaris, ordenats per percentatge de partides
  guanyades.

La classe `Arena` ha de controlar, com a mínim, aquestes restriccions:

- Només els usuaris registrats (i no doants de baixa) poden jugar partides.

- Per jugar una partida cal estat connectat a l'aplicació.

- Només es pot jugar una partida alhora.

- No es pot jugar contra un mateix.

Si vols, considera implementar un senzill sistema de persistència de dades que permeti desar i recuperar un objecte `Arena` a/des d'un fitxer usant el mòdul `pickle` (vegeu [les lliçons](https://lliçons.jutge.org/python/fitxers/#serialitzacio-d-objectes)).

És responsabilitat teva definir la interfície de la classe `Arena` i com gestionar les restriccions en la seva implemetació. La classe ha de ser tant senzilla i fàcil d'utilitzar com sigui possible (pensa que el servidor és una simple capa d'entrada/sortida via xarxa que la faria servir).

Per implementar aquesta classe tingues en compte que es preveu que el sistema tindrà molts usuaris i que aquests jugaran moltes partides. Per tant, cal que el sistema sigui eficient i que els jugadors trobin que el sistema és ràpid.

Per senzillesa, no cal que enforcis restriccions de temps per jugar una partida. Tampoc cal que implementis cap sistema de seguretat ni privacitat, se suposa que això recau al nivell superior.

## Esquelet

Al directori [backgammon](backgammon) pots descarregar l'esquelet dels mòduls del projecte amb algunes funcionalitats ja implementades.

## Avaluació

L'avaluació de la teva pràctica tindrà en compte diversos aspectes clau, entre els quals es destaquen els següents:

1. **Qualitat del codi**: S'examinarà el codi font tenint en compte diversos factors, com ara la _correctesa_, la _completitud_, la _llegibilitat_, l'_eficiència_, el _bon ús dels identificadors_, ètc. També es tindrà en compte la _bona estructuració_ del codi, és a dir, l'ús adequat de funcions, classes, mòduls i altres elements que afavoreixin la redacció, la comprensió i el manteniment del codi a llarg termini. Es valorarà negativament l'ús de funcions llargues o poc clares, funcions incomprensibles sense especificació, la presència de codi duplicat o innecessari, acoblament fort, variables globals o atributs de classe erronis, comentaris excessius, i altres pràctiques nocives. Les funcions de la classe `Arena` han de ser raonablament eficients i no s'admetran disbarats. Totes les funcions han de tenir anotacions de tipus i, idealment, `mypy` no hauria de donar cap diagnòstic.

2. **Qualitat de la documentació**: S'analitzarà la documentació del projecte, amb especial atenció a la seva _claredat_, _precisió_ i _completesa_, alhora que la seva _concisió_. La documentació hauria de descriure adequadament el funcionament del codi, les seves funcions i característiques principals, així com qualsevol altre aspecte rellevant que faciliti la comprensió i l'ús del projecte. La documentació també ha de deixar clares les decisions de disseny preses. Cal separar l'especificació de les classes, funcions i mètodes (què fan) dels comentaris sobre el codi (com es fa). El `readme` ha d'estar en format Markdown i ha d'aportar tots els elements necessaris.

3. **Qualitat dels jocs de proves**: Es valorarà l'_existència_, la _cobertura_ i la _fiabilitat_ dels jocs de proves dissenyats per verificar el correcte funcionament del codi. Els jocs de proves han de ser suficientment amplis i variats per garantir que el codi respon de manera adequada a diferents situacions i casos d'ús. Tanmateix, els jocs de proves han de ser _limitats_, _concisos_ i _eficaços_, evitant la redundància i la repetició innecessària. Alhora, el propòsit dels jocs de proves ha de ser _fàcil de comprendre_. Han de ser fàcils d'_executar_, i han de proporcionar una _sortida clara_ que permeti identificar ràpidament qualsevol problema o error.

En definitiva, és important recordar que es tracta d'un projecte de programació i, per tant, s'espera que el codi segueixi totes les _bones pràctiques de programació_ que s'han ensenyat a AP1 i AP2.

# Desenvolupament de la pràctica

Aquesta pràctica té dues parts:

1.  A la primera part has d'implementar els mòduls descrits.

    Has de lliurar la pràctica a través de l'aplicació **Mussol**. Per a fer-ho, vés a https://mussol.jutge.org, identifica't amb el teu usuari oficial de la UPC (acabat amb `@estudiantat.upc.edu`) i la teva contrasenya de Jutge.org i tria l'activitat "AP2 2025 Backgammon". Has de lliurar un fitzer `zip` amb els continguts que es descriuen més tard.

    Compte: Has de tenir cura de **NO** identificar els continguts lliurats amb el teu nom o altre informació personal teva: el teu lliurament ha de ser completament anònim. Això també s'aplica als noms dels fitxers.

    La data límit per lliurar la primera part de la teva pràctica és el divendres 28 de març fins a les 15:00.

2.  A la segona part de la pràctica has de corregir tres pràctiques d'altres companys. Aquesta correcció es farà també a través de **Mussol** i implicarà valorar diferents rúbriques que només veuràs en aquest punt.

    L'avaluació també serà anònima. El sistema calcularà automàticament la teva nota i també avisarà als professors de possibles incoherències. Els abusos seran penalitzats.

    Cada estudiant té el dret de rebutjar la nota calculada a partir de la informació rebuda dels seus companys i pot demanar l'avaluació per part d'un professor (qui podrà puntuar a l'alta o a la baixa respecte l'avaluació dels estudiants). Els professors també poden corregir pràctiques "d'ofici" i substituir la nota calculada per la del professor.

    Pots començar a corregir les pràctiques dels teus companys a partir del dilluns 31 de març a les 15:00. La data límit per lliurar la segona part de la teva pràctica és el dimecres 23 d'abril a les 15:00. No podràs veure les correccions dels teus companys fins al divendres 25 d'abril a les 15:00.

Totes les pràctiques s'han de fer en solitari. Els professors utilitzaran programes detectors de plagi. És obligatori corregir les pràctiques dels tres companys assignades pel **Mussol**. Els terminis de lliurament són improrrogables.

## Lliurament

Lliura la teva pràctica al Mussol en un fitzer `.zip` que contigui:

- Tots els fitxers `.py` necessaris.

- Un fitxer `README.md` escrit en Markdown que contingui la informació de la teva pràctica. Consulta https://www.markdownguide.org/cheat-sheet/ i https://www.makeareadme.com/ per exemple.

- Si cal, imatges a `images/*.png` per complementar el `README.md`.

El fitxer `.zip` no ha de contenir res més.

# Consells

- Comprova que cada part que fas funciona correctament, documenta el teu codi amb els comentaris necessaris i sense comentaris innecessaris i especifica totes les classes i mètodes amb _docstrings_. Escriu jocs de proves útils.

- Assegura't que el teu programa inclou els tipus de tots els paràmetres i resultats a totes les funcions i que no hi ha errors de tipus amb `mypy`.

- Per evitar problemes de còpies, no pengis el teu projecte en repositoris públics.

- No esperis al darrer moment per fer el lliurement.

  De debò.

  No, no és bona idea: El cafè que t'has preparat per mantenir-te despert et caurà damunt del teclat, la corrent marxarà al darrer moment, l'internet caurà cinc minuts abans del _deadline_, l'ordinador on tenies el projecte (del qual mai has còpies de seguretat) et caurà a terra i es trencarà en mil bocins... Tot això ha passat. El **Mussol** no et deixarà fer lliuraments passats els terminis. Pots fer múltiples lliuraments, el definitiu sempre és el darrer.

# Autors

Jordi Petit

©️ Universitat Politècnica de Catalunya, 2025
