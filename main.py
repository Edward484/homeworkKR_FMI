import copy
import random
import sys
import time
import signal


# informatii despre un nod din arborele de parcurgere (nu din graful initial)
import stopit as stopit


class NodParcurgere:
    def __init__(self, info, parinte, cost=0,mesaj = "", h=0):
        self.info = info
        self.parinte = parinte
        self.g = cost
        self.h = h
        self.mesaj = mesaj
        self.f = self.g + self.h

    def obtineDrum(self):
        l = [self];
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self, afisCost=False, afisLung=False):  # returneaza si lungimea drumului
        l = self.obtineDrum()
        for i, nod in enumerate(l):
            print(i + 1, ")\n",nod.mesaj,sep="")
            print(str(nod), sep="")
        if afisCost:
            print("Cost: ", self.g)
        if afisCost:
            print("Lungime: ", len(l))
        return len(l)

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if (infoNodNou == nodDrum.info):
                return True
            nodDrum = nodDrum.parinte

        return False

    def __repr__(self):
        sir = ""
        sir += str(self.info)
        return (sir)


    def __str__(self):
        sir = ""
        for i, linie in enumerate(self.info):
            sir += f"{i} :  "
            sir += " ".join([str(elem) for elem in linie]) + "\n"
        sir += "\n"
        return sir


class Graph:  # graful problemei
    def __init__(self, nume_fisier):
        f = open(nume_fisier, "r")
        sirFisier = f.read()
        try:
            listaLinii = sirFisier.strip().split("\n")
            self.combinare_culori = []
            self.costuri_culori = {}
            self.start = []
            self.scopuri = []
            self.max_capacitate = 0

            stare_finala = False
            stare_initiala = False
            combination_is_finished = False

            for linie in listaLinii:
                culori = []
                culori = linie.split(" ")

                if len(culori) == 3 and combination_is_finished == False and stare_initiala == False and stare_finala == False:
                    self.combinare_culori.append((culori[0], culori[1], culori[2]))
                    self.combinare_culori.append((culori[1], culori[0], culori[2]))


                if len(culori) == 2 and stare_initiala == False and stare_finala == False:
                    combination_is_finished = True
                    self.costuri_culori[culori[0]] = int(culori[1])

                if stare_initiala == True:
                    if(culori[0] != "stare_finala") :
                        if self.max_capacitate < int(culori[0]):
                            self.max_capacitate = int(culori[0])

                    if len(culori) == 3:
                        self.start.append((int(culori[0]), int(culori[1]), culori[2]))
                    if len(culori) == 2:
                        self.start.append((int(culori[0]), int(culori[1]), "gol"))

                if stare_finala == True:
                    self.scopuri.append((int(culori[0]), culori[1]))

                if culori[0] == "stare_initiala":
                    stare_initiala = True

                if culori[0] == "stare_finala":
                    stare_initiala = False
                    stare_finala = True
            t = 1
            self.cost_max = max(self.costuri_culori.values())


        except:
            print("Eroare la parsare!")
            sys.exit(0)

    def testeaza_scop(self, nodCurent):
        s = 0
        for vas_scop in self.scopuri:
            for vas_curent in nodCurent.info:
                if vas_scop[0] == vas_curent[1] and vas_scop[1] == vas_curent[2]:
                    s+=1
                    break
        if s == len(self.scopuri):
            return True
        return False

    # nr inversiuni trebuie sa fie par ca sa putem ajunge in starea finala
    def areSolutii(self, infoNod):
        ok_1 = False
        ok_2 = False
        for scop in self.scopuri:
            ok_1 = False
            ok_2 = False
            #cautam sa vedem daca culoarea scop e intr-unul din vasele initiale si daca cantitatea ceruta incape in vas
            for vas_initial in self.start:
                if scop[1] == vas_initial[2] and scop[0] <= vas_initial[0]:
                    ok_1 = True
            #cautam daca se poate face culoarea
            for combinatie in self.combinare_culori:
                if scop[1] == combinatie[2]:
                    ok_1 = True
            for vas_initial in self.start:
                if scop[0] < vas_initial[0]:
                    ok_2 = True
            if ok_2 == False or ok_1 == False:
                return False
        return ok_1 or ok_2

    # va genera succesorii sub forma de noduri in arborele de parcurgere

    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica banala"):
        listaSuccesori = []
        for i_t , vas_turnator in enumerate(nodCurent.info):
            for i_p, vas_primitor in enumerate(nodCurent.info):
                if vas_primitor != vas_turnator:
                    litri_ramasi_vas_primitor = vas_primitor[0] - vas_primitor[1]
                    if litri_ramasi_vas_primitor > 0 and vas_turnator[1] > 0:
                        #se poate creea o noua stare

                        #realizam copia starii
                        newInfo = []
                        new_vas_primitor = 0
                        new_vas_turnator = 0
                        litri_turnati = 0
                        mesaj = ""

                        if vas_turnator[1] > litri_ramasi_vas_primitor:
                            #se umple vasul în care turnam
                            new_vas_primitor = (vas_primitor[0], vas_primitor[0], gr.combina_culori(vas_primitor[2], vas_turnator[2]))
                            new_vas_turnator = (vas_turnator[0], vas_turnator[1] - litri_ramasi_vas_primitor, vas_turnator[2])
                            litri_turnati = vas_primitor[0] - vas_primitor[1]
                            mesaj = f"Din vasul {i_t} s-au turnat {litri_turnati} de {vas_turnator[2]} in vasul {i_p} "

                        if vas_turnator[1] <= litri_ramasi_vas_primitor:
                            #se goleste vasul din care turnam
                            new_vas_primitor = (vas_primitor[0], vas_primitor[1] + vas_turnator[1], gr.combina_culori(vas_primitor[2], vas_turnator[2]) )
                            new_vas_turnator = (vas_turnator[0], 0, "gol")
                            litri_turnati = vas_turnator[1]
                            mesaj = f"Din vasul {i_t} s-au turnat {litri_turnati} litri de {vas_turnator[2]} in vasul {i_p} "


                        for vas in nodCurent.info:
                            if vas != vas_turnator and vas != vas_primitor:
                                newInfo.append(vas)
                            if vas == vas_turnator:
                                newInfo.append(new_vas_turnator)
                            if vas == vas_primitor:
                                newInfo.append(new_vas_primitor)

                        cost = 0
                        if vas_turnator[2] != "nedefinit" and new_vas_primitor[2] != "nedefinit" and vas_primitor[2] != "nedefinit" :
                            cost = litri_turnati * self.costuri_culori[vas_turnator[2]]
                        if new_vas_primitor[2] == "nedefinit" and vas_primitor[2] != "nedefinit" and vas_turnator[2] != "nedefinit":
                            cost = litri_turnati * self.costuri_culori[vas_turnator[2]] + vas_primitor[1] * self.costuri_culori[vas_primitor[2]]
                        if vas_turnator[2] == "nedefinit":
                            cost = litri_turnati
                        if vas_primitor[2] == "nedefinit":
                            cost += vas_primitor[1]
                        mesaj += f"cu costul {cost}."
                        listaSuccesori.append(NodParcurgere(newInfo, nodCurent, nodCurent.g + cost,mesaj, self.calculeaza_h(newInfo, tip_euristica)))
        return listaSuccesori

    def combina_culori(self, culoare1, culoare2):
        if culoare1 == "gol" :
            return culoare2
        if culoare2 == "gol" :
            return culoare1
        for linie in self.combinare_culori:
            if linie[0] == culoare1 and linie[1] == culoare2:
                return linie[2]
        if culoare2 == culoare1:
            return culoare1
        return "nedefinit"

    def calculeaza_h(self, infoNod, tip_euristica="euristica banala"):
        if infoNod in self.scopuri:
            return 0
        if tip_euristica == "euristica banala":
            return 1
        if tip_euristica == "euristica 1":
            s = 0
            for vas_scop in self.scopuri:
                for vas_curent in infoNod:
                    if vas_scop[0] == vas_curent[1] and vas_scop[1] == vas_curent[2]:
                        s += 1
            return len(self.scopuri) - s

        if tip_euristica == "euristica 2":
            h = 0
            for vas_scop in self.scopuri:
                for vas_curent in infoNod:
                    if vas_scop[1] == vas_curent[2] and vas_curent[0] >= vas_scop[0]:
                        h+= abs(vas_scop[0] - vas_curent[1])
                        break
            return h

        if tip_euristica == "euristica neadmisibila":
            h = 0
            for vas_scop in self.scopuri:
                for vas_curent in infoNod:
                    if vas_scop[0] != vas_curent[1] and vas_scop[1] != vas_curent[2]:
                        h += random.randrange(self.cost_max * self.max_capacitate * 4, self.cost_max * self.max_capacitate * 5  )
            return h


    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return (sir)



def a_star(gr, NSOL, tip_euristica):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    if gr.areSolutii(gr.start) == False:
        print("Nu are solutii!")
        return
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, tip_euristica))]
    stop_generate = False
    max_c = 1
    total_succesori = 0
    while len(c) > 0:
        if len(c) > max_c:
            max_c = len(c)
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            print("Solutie: ")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            print(time.time() - t1, "secunde")
            print(f"nr maxim noduri in memorie: {max_c}")
            print(f"nr total de noduri calculate: {total_succesori}")
            print("\n----------------\n")
            NSOL -= 1
            if NSOL == 0:
                return
        if len(c) < 5000 and stop_generate == False:
            lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
            total_succesori += len(lSuccesori)

        if len(c) > 5000:
            stop_generate = True
            lSuccesori = []

        for s in lSuccesori:
            i = 0
            gasit_loc = False

            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez dupa f
                if c[i].f >= s.f:
                    gasit_loc = True
                    break
            if gasit_loc:
                if s not in c:
                    c.insert(i, s)
                else:
                    t = 1
            else:
                if s not in c:
                    c.append(s)
                else:
                    t = 1


def a_star2(gr,NSOL, tip_euristica):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    l_open = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]

    # l_open contine nodurile candidate pentru expandare (este echivalentul lui c din A* varianta neoptimizata)

    # l_closed contine nodurile expandate
    l_closed = []
    max_l_open = 1
    total_succesori = 0

    while len(l_open) > 0:
        if len(l_open) > max_l_open:
            max_l_open = len(l_open)
        nodCurent = l_open.pop(0)
        l_closed.append(nodCurent)
        if gr.testeaza_scop(nodCurent):
            print("Solutie: ")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            print(time.time() - t1, "secunde")
            print(f"nr maxim noduri in memorie: {max_l_open}")
            print(f"nr total de noduri calculate: {total_succesori}")
            print("\n----------------\n")
            NSOL -= 1
            if NSOL == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica)
        total_succesori += len(lSuccesori)

        for s in lSuccesori:
            gasitC = False
            for nodC in l_open:
                if s.info == nodC.info:
                    gasitC = True
                    if s.f >= nodC.f:
                        lSuccesori.remove(s)
                    else:  # s.f<nodC.f
                        l_open.remove(nodC)
                    break
            if not gasitC:
                for nodC in l_closed:
                    if s.info == nodC.info:
                        if s.f >= nodC.f:
                            lSuccesori.remove(s)
                        else:  # s.f<nodC.f
                            l_closed.remove(nodC)
                        break
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(l_open)):
                # diferenta fata de UCS e ca ordonez crescator dupa f
                # daca f-urile sunt egale ordonez descrescator dupa g
                if l_open[i].f > s.f or (l_open[i].f == s.f and l_open[i].g <= s.g):
                    gasit_loc = True
                    break
            if gasit_loc:
                l_open.insert(i, s)
            else:
                l_open.append(s)

def ida_star(gr, NSOL):
    nodStart = NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))
    total_succesori = 0

    limita = nodStart.f
    while True:

        NSOL, rez = construieste_drum(gr, nodStart, limita, NSOL, total_succesori)
        if rez == "gata":
            break
        if rez == float('inf'):
            break
        limita = rez

def construieste_drum(gr, nodCurent, limita, NSOL,total_succesori):
    if nodCurent.f > limita:
        return NSOL, nodCurent.f
    if gr.testeaza_scop(nodCurent) and nodCurent.f == limita:
        print("Solutie: ")
        nodCurent.afisDrum(afisCost=True, afisLung=True)
        print(time.time() - t1, "secunde")
        print(f"limita: {limita}")
        print(f"nr total de noduri calculate: {total_succesori}")
        print("\n----------------\n")
        NSOL -= 1
        if NSOL == 0:
            return 0, "gata"
    lSuccesori = gr.genereazaSuccesori(nodCurent)
    total_succesori+=len(lSuccesori)
    minim = float('inf')
    for s in lSuccesori:
        NSOL, rez = construieste_drum(gr, s, limita, NSOL, total_succesori)
        if rez == "gata":
            return 0, "gata"
        if rez < minim:
            minim = rez
    return NSOL, minim

def breadth_first(gr, NSOL):
    c = [NodParcurgere(gr.start, None)]
    max_c = 1
    total_succesori = 0

    while len(c) > 0:
        nodCurent = c.pop(0)
        if len(c) > max_c:
            max_c = len(c)

        if gr.testeaza_scop(nodCurent):
            print("Solutie: ")
            nodCurent.afisDrum(afisCost=True, afisLung=True)
            print(time.time() - t1, "secunde")
            print(f"nr maxim noduri in memorie: {max_c}")
            print(f"nr total de noduri calculate: {total_succesori}")
            print("\n----------------\n")
            NSOL -= 1
            if NSOL == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        total_succesori += len(lSuccesori)
        c.extend(lSuccesori)

def uniform_cost(gr, NSOL=1):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]
    max_c = 1
    total_succesori = 0

    while len(c) > 0:
        if len(c) > max_c:
            max_c = len(c)
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            print("Solutie: ", end="")
            nodCurent.afisDrum()
            print(f"nr maxim noduri in memorie: {max_c}\n")
            print(f"nr =total de noduri calculate: {max_c}\n")
            print("\n----------------\n")
            NSOL -= 1
            if NSOL == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        total_succesori += len(lSuccesori)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                if c[i].g > s.g:
                    gasit_loc = True
                    break;
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)


@stopit.threading_timeoutable(default="intrat in timeout")
def solve(NSOL):


    return "functie finalizata"




if __name__ == "__main__":
    print("Enter the input path:")
    #input_path = input()
    print("Enter the output path:")
    #/output_path = input()
    print("Enter the maximum number of solutions:")
    #NSOL = int(input())
    NSOL = 3
    print("Enter the timeout time:")
    #timeout_time = int(input())

    gr = Graph("input_already_final.txt")

    print("\n\n##################\nSolutii obtinute cu A*:")
    t1 = time.time()

    s = 1
    while s != 0:
        print("Alege un algoritm cu care sa rulezi problema:")
        print("0 - STOP")
        print("1 - BF")
        print("2 - DF")
        print("3 - DFI")
        print("4 - A*")
        print("5 - A* optimizat")
        print("6 - Uniform cost")
        print("7 - IDA*")
        print("ALegerea ta: ", end="")
        s = int(input())
        if s == 1:
            breadth_first(gr, NSOL=NSOL)

        if s == 4:
            a_star(gr, NSOL=NSOL, tip_euristica="euristica 2")
        if s == 5:
            a_star2(gr, NSOL=NSOL, tip_euristica="euristica 2")
        if s == 6:
            uniform_cost(gr, NSOL=NSOL)
        if s == 7:
            ida_star(gr, NSOL=NSOL)
    rez = solve(3, timeout=10)
    print("\nRezultat functie: {}".format(rez))

