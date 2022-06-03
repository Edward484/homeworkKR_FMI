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

    def afisDrum(self,f, afisCost=False, afisLung=False):  # returneaza si lungimea drumului
        l = self.obtineDrum()
        for i, nod in enumerate(l):
            f.writelines(f"{i + 1}) \n")
            f.write(f"{nod.mesaj}\n")
            f.write(str(nod))
        if afisCost:
            f.write(f"Cost:  {self.g}\n")
        if afisCost:
            f.write(f"Lungime:  {len(l)}\n")
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
                            new_vas_primitor = (vas_primitor[0], vas_primitor[0], self.combina_culori(vas_primitor[2], vas_turnator[2]))
                            new_vas_turnator = (vas_turnator[0], vas_turnator[1] - litri_ramasi_vas_primitor, vas_turnator[2])
                            litri_turnati = vas_primitor[0] - vas_primitor[1]
                            mesaj = f"Din vasul {i_t} s-au turnat {litri_turnati} de {vas_turnator[2]} in vasul {i_p} "

                        if vas_turnator[1] <= litri_ramasi_vas_primitor:
                            #se goleste vasul din care turnam
                            new_vas_primitor = (vas_primitor[0], vas_primitor[1] + vas_turnator[1], self.combina_culori(vas_primitor[2], vas_turnator[2]) )
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


@stopit.threading_timeoutable(default="intrat in timeout")
def a_star(gr, NSOL, tip_euristica,output_path):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    if gr.areSolutii(gr.start) == False:
        with open(output_path, 'a') as f:
            f.write("Nu are solutii!\n")
            return "functie finalizata"
    c = [NodParcurgere(gr.start, None, 0,"", gr.calculeaza_h(gr.start, tip_euristica))]
    stop_generate = False
    max_c = 1
    total_succesori = 0
    while len(c) > 0:
        if len(c) > max_c:
            max_c = len(c)
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            with open(output_path, 'a') as f:
                f.writelines("Solutie: \n")
                nodCurent.afisDrum(f, afisCost=True, afisLung=True)
                f.writelines(f"{time.time() - t1} secunde\n")

                f.writelines(f"nr maxim noduri in memorie: {max_c}\n")
                f.writelines(f"nr total de noduri calculate: {total_succesori}\n")
                f.writelines("\n----------------\n")
                NSOL -= 1
                if NSOL == 0:
                    return "functie finalizata"
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

@stopit.threading_timeoutable(default="intrat in timeout")
def a_star2(gr,NSOL, tip_euristica, output_path):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    l_open = [NodParcurgere(gr.start, None, 0,"", gr.calculeaza_h(gr.start))]

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
            with open(output_path, 'a') as f:
                f.writelines("Solutie: \n")
                nodCurent.afisDrum(f, afisCost=True, afisLung=True)
                f.writelines(f"{time.time() - t1} secunde\n")

                f.writelines(f"nr maxim noduri in memorie: {max_l_open}\n")
                f.writelines(f"nr total de noduri calculate: {total_succesori}\n")
                f.writelines("\n----------------\n")
                NSOL -= 1
                if NSOL == 0:
                    return "functie finalizata"
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

@stopit.threading_timeoutable(default="intrat in timeout")
def ida_star(gr, NSOL,tip_euristica,output_path):
    nodStart = NodParcurgere(gr.start, None, 0,"", gr.calculeaza_h(gr.start,tip_euristica))
    total_succesori = 0

    limita = nodStart.f
    while True:

        NSOL, rez = construieste_drum(gr, nodStart, limita, NSOL, total_succesori,tip_euristica,output_path)
        if rez == "functie finalizata":
            return "functie finalizata"
        if rez == float('inf'):
            break
        limita = rez

def construieste_drum(gr, nodCurent, limita, NSOL,total_succesori,tip_euristica,output_path):
    if nodCurent.f > limita:
        return NSOL, nodCurent.f
    if gr.testeaza_scop(nodCurent):
        with open(output_path, 'a') as f:
            f.writelines("Solutie: \n")
            nodCurent.afisDrum(f, afisCost=True, afisLung=True)
            f.writelines(f"{time.time() - t1} secunde\n")
            f.writelines(f"nr total de noduri calculate: {total_succesori}\n")
            f.writelines("\n----------------\n")
            NSOL -= 1
            if NSOL == 0:
                return "functie finalizata", "functie finalizata"
    lSuccesori = gr.genereazaSuccesori(nodCurent,tip_euristica)
    total_succesori+=len(lSuccesori)
    minim = float('inf')
    for s in lSuccesori:
        NSOL, rez = construieste_drum(gr, s, limita, NSOL, total_succesori,tip_euristica,output_path)
        if rez == "functie finalizata":
            return 0, "functie finalizata"
        if rez < minim:
            minim = rez
    return NSOL, minim

@stopit.threading_timeoutable(default="intrat in timeout")
def breadth_first(gr, NSOL,output_path):
    c = [NodParcurgere(gr.start, None)]
    max_c = 1
    total_succesori = 0

    while len(c) > 0:
        nodCurent = c.pop(0)
        if len(c) > max_c:
            max_c = len(c)

        if gr.testeaza_scop(nodCurent):
            with open(output_path,'a') as f:
                f.writelines("Solutie: \n")
                nodCurent.afisDrum(f,afisCost=True, afisLung=True)
                f.writelines(f"{time.time() - t1} secunde\n")

                f.writelines(f"nr maxim noduri in memorie: {max_c}\n")
                f.writelines(f"nr total de noduri calculate: {total_succesori}\n")
                f.writelines("\n----------------\n")
                NSOL -= 1
                if NSOL == 0:
                    return "functie finalizata"
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        total_succesori += len(lSuccesori)
        c.extend(lSuccesori)


@stopit.threading_timeoutable(default="intrat in timeout")
def uniform_cost(gr, NSOL=1, output_path = "/o6/output.txt"):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    c = [NodParcurgere(gr.start, None, 0,"", gr.calculeaza_h(gr.start))]
    max_c = 1
    total_succesori = 0

    while len(c) > 0:
        if len(c) > max_c:
            max_c = len(c)
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            with open(output_path, 'a') as f:
                f.writelines("Solutie: \n")
                nodCurent.afisDrum(f, afisCost=True, afisLung=True)
                f.writelines(f"{time.time() - t1} secunde\n")
                f.writelines(f"nr maxim noduri in memorie: {max_c}\n")
                f.writelines(f"nr total de noduri calculate: {total_succesori}\n")
                f.writelines("\n----------------\n")
                NSOL -= 1
                if NSOL == 0:
                    return "functie finalizata"
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
def depth_first(gr,NSOL,output_path):
    # vom simula o stiva prin relatia de parinte a nodului curent
    import sys
    sys.setrecursionlimit(1000)
    try:
        df(NodParcurgere(gr.start, None, 0,"", gr.calculeaza_h(gr.start)),gr,NSOL,0,0,output_path)
    except:
        pass

continua = True

def df(nodCurent,gr,NSOL,total_succesori,max_c,output_path):
    global continua
    if not continua:
        return
    if gr.testeaza_scop(nodCurent):
        with open(output_path, 'a') as f:
            f.writelines("Solutie: \n")
            nodCurent.afisDrum(f, afisCost=True, afisLung=True)
            f.writelines(f"{time.time() - t1} secunde\n")

            f.writelines(f"nr maxim noduri in memorie: {max_c}\n")
            f.writelines(f"nr total de noduri calculate: {total_succesori}\n")
            f.writelines("\n----------------\n")
            NSOL -= 1
            if NSOL == 0:
                return "functie finalizata"

    lSuccesori = gr.genereazaSuccesori(nodCurent)
    total_succesori += len(lSuccesori)
    for sc in lSuccesori:
        df(sc,gr,NSOL,total_succesori,max_c+1,output_path)

@stopit.threading_timeoutable(default="intrat in timeout")
def depth_first_iterative_deepening(gr,NSOL,adancimeMax,output_path):
  #vom simula o stiva prin relatia de parinte a nodului curent
  for i in range(1, adancimeMax):
      with open(output_path, 'a') as f:
          f.write(f"Adancime maxima:  {i} \n")
          dfi(i, NodParcurgere(gr.start, None, 0,"", gr.calculeaza_h(gr.start)),NSOL, gr, 0,0,output_path)

# ca functia df doar ca impunem si o lungime maxima a drumului
def dfi(adMaxCurenta, nodCurent, NSOL,gr,total_succesori,max_c,output_path):
    global continua
  #descrestem adMaxCurenta pana la 0
    if adMaxCurenta<=0 or not continua: #ar trebui adMaxCurenta sa nu ajunga niciodata < 0
        return
    adMaxCurenta -= 1

    if gr.testeaza_scop(nodCurent):
        with open(output_path, 'a') as f:
            f.writelines("Solutie: \n")
            nodCurent.afisDrum(f, afisCost=True, afisLung=True)
            f.writelines(f"{time.time() - t1} secunde\n")

            f.writelines(f"nr maxim noduri in memorie: {max_c}\n")
            f.writelines(f"nr total de noduri calculate: {total_succesori}\n")
            f.writelines("\n----------------\n")
            NSOL -= 1
            if NSOL == 0:
                return "functie finalizata"
    lSuccesori=gr.genereazaSuccesori(nodCurent)
    total_succesori += len(lSuccesori)
    for sc in lSuccesori:
        dfi(adMaxCurenta, sc, NSOL, gr,total_succesori, max_c+1,output_path)

def callBF(NSOL, input_path, output_path,timeout_time):
    gr1 = Graph(input_path + "/input.txt")
    rez1 = breadth_first(gr1, NSOL=NSOL, output_path=output_path + "/output.txt", timeout = timeout_time)

    gr2 = Graph(input_path + "/input_already_final.txt")
    rez2 = breadth_first(gr2, NSOL=NSOL, output_path=output_path + "/output_already_final.txt", timeout = timeout_time)

    gr3 = Graph(input_path + "/input_no_sol.txt")
    rez3 = breadth_first(gr3, NSOL=NSOL, output_path=output_path + "/output_no_sol.txt", timeout = timeout_time)

    gr4 = Graph(input_path + "/input_timeout.txt")
    rez4 = breadth_first(gr4, NSOL=NSOL, output_path=output_path + "/output_timeout.txt", timeout = timeout_time)
    print("\nRezultat functie: {}".format(rez1))
    print("\nRezultat functie: {}".format(rez2))
    print("\nRezultat functie: {}".format(rez3))
    print("\nRezultat functie: {}".format(rez4))

def callDF(NSOL, input_path, output_path,timeout_time):
    global continua

    continua = True
    gr1 = Graph(input_path + "/input.txt")
    rez1 = depth_first(gr1, NSOL=NSOL, output_path=output_path + "/output.txt", timeout = timeout_time)

    continua = True
    gr2 = Graph(input_path + "/input_already_final.txt")
    rez2 = depth_first(gr2, NSOL=NSOL, output_path=output_path + "/output_already_final.txt", timeout = timeout_time)

    continua = True
    gr3 = Graph(input_path + "/input_no_sol.txt")
    rez3 = depth_first(gr3, NSOL=NSOL, output_path=output_path + "/output_no_sol.txt", timeout = timeout_time)

    continua = True
    gr4 = Graph(input_path + "/input_timeout.txt")
    rez4 = depth_first(gr4, NSOL=NSOL, output_path=output_path + "/output_timeout.txt", timeout = timeout_time)
    print("\nRezultat functie: {}".format(rez1))
    print("\nRezultat functie: {}".format(rez2))
    print("\nRezultat functie: {}".format(rez3))
    print("\nRezultat functie: {}".format(rez4))

def callDFI(NSOL, input_path, output_path, adancimeMax,timeout_time):
    global continua

    continua = True
    gr1 = Graph(input_path + "/input.txt")
    rez1 = depth_first_iterative_deepening(gr1, NSOL=NSOL, adancimeMax=adancimeMax, output_path=output_path + "/output.txt", timeout=timeout_time)

    continua = True
    gr2 = Graph(input_path + "/input_already_final.txt")
    rez2 = depth_first_iterative_deepening(gr2, NSOL=NSOL, adancimeMax=adancimeMax, output_path=output_path + "/output_already_final.txt", timeout=timeout_time)

    continua = True
    gr3 = Graph(input_path + "/input_no_sol.txt")
    rez3 = depth_first_iterative_deepening(gr3, NSOL=NSOL, adancimeMax=adancimeMax, output_path=output_path + "/output_no_sol.txt", timeout=timeout_time)

    continua = True
    gr4 = Graph(input_path + "/input_timeout.txt")
    rez4 = depth_first_iterative_deepening(gr4, NSOL=NSOL, adancimeMax=adancimeMax, output_path=output_path + "/output_timeout.txt", timeout=timeout_time)
    print("\nRezultat functie: {}".format(rez1))
    print("\nRezultat functie: {}".format(rez2))
    print("\nRezultat functie: {}".format(rez3))
    print("\nRezultat functie: {}".format(rez4))

def callAStar(NSOL, input_path, output_path,timeout_time):
    print("Euristica dorita:", end="")
    euristica = input()
    gr1 = Graph(input_path + "/input.txt")
    rez1 = a_star(gr1, NSOL=NSOL, tip_euristica=euristica, output_path=output_path + "/output.txt", timeout = timeout_time)

    gr2 = Graph(input_path + "/input_already_final.txt")
    rez2 = a_star(gr2, NSOL=NSOL, tip_euristica=euristica, output_path=output_path + "/output_already_final.txt", timeout=timeout_time)

    gr3 = Graph(input_path + "/input_no_sol.txt")
    rez3 = a_star(gr3, NSOL=NSOL, tip_euristica=euristica, output_path=output_path + "/output_no_sol.txt", timeout=timeout_time)

    gr4 = Graph(input_path + "/input_timeout.txt")
    rez4 = a_star(gr4, NSOL=NSOL, tip_euristica=euristica, output_path=output_path + "/output_timeout.txt", timeout=timeout_time)
    print("\nRezultat functie: {}".format(rez1))
    print("\nRezultat functie: {}".format(rez2))
    print("\nRezultat functie: {}".format(rez3))
    print("\nRezultat functie: {}".format(rez4))

def callAStar2(NSOL, input_path, output_path,timeout_time):
    print("Eursitica dorita:", end="")
    euristica = input()
    gr1 = Graph(input_path + "/input.txt")
    rez1 = a_star2(gr1, NSOL=NSOL, tip_euristica=euristica, output_path=output_path + "/output.txt", timeout=timeout_time)

    gr2 = Graph(input_path + "/input_already_final.txt")
    rez2 = a_star2(gr2, NSOL=NSOL, tip_euristica=euristica, output_path=output_path + "/output_already_final.txt", timeout=timeout_time)

    gr3 = Graph(input_path + "/input_no_sol.txt")
    rez3 = a_star2(gr3, NSOL=NSOL, tip_euristica=euristica, output_path=output_path + "/output_no_sol.txt", timeout=timeout_time)

    gr4 = Graph(input_path + "/input_timeout.txt")
    rez4 = a_star2(gr4, NSOL=NSOL, tip_euristica=euristica, output_path=output_path + "/output_timeout.txt", timeout=timeout_time)
    print("\nRezultat functie: {}".format(rez1))
    print("\nRezultat functie: {}".format(rez2))
    print("\nRezultat functie: {}".format(rez3))
    print("\nRezultat functie: {}".format(rez4))

def callUnif(NSOL, input_path, output_path,timeout_time):
    gr1 = Graph(input_path + "/input.txt")
    rez1 = uniform_cost(gr1, NSOL=NSOL, output_path=output_path + "/output.txt", timeout=timeout_time)

    gr2 = Graph(input_path + "/input_already_final.txt")
    rez2 = uniform_cost(gr2, NSOL=NSOL, output_path=output_path + "/output.txt", timeout = timeout_time)

    gr3 = Graph(input_path + "/input_no_sol.txt")
    rez3 = uniform_cost(gr3, NSOL=NSOL, output_path=output_path + "/output.txt", timeout = timeout_time)

    gr4 = Graph(input_path + "/input_timeout.txt")
    rez4 = uniform_cost(gr4, NSOL=NSOL, output_path=output_path + "/output.txt", timeout = timeout_time)
    print("\nRezultat functie: {}".format(rez1))
    print("\nRezultat functie: {}".format(rez2))
    print("\nRezultat functie: {}".format(rez3))
    print("\nRezultat functie: {}".format(rez4))

def callIdaStar(NSOL, input_path, output_path,timeout_time):
    print("Eursitica dorita:", end="")
    euristica = input()
    gr1 = Graph(input_path + "/input.txt")
    rez1 = ida_star(gr1, NSOL=NSOL, tip_euristica=euristica, output_path=output_path + "/output.txt", timeout=timeout_time)

    gr2 = Graph(input_path + "/input_already_final.txt")
    rez2 = ida_star(gr2, NSOL=NSOL, tip_euristica=euristica,  output_path=output_path + "/output_already_final.txt",
                    timeout=timeout_time)

    gr3 = Graph(input_path + "/input_no_sol.txt")
    rez3 = ida_star(gr3, NSOL=NSOL, tip_euristica=euristica,  output_path=output_path + "/output_no_sol.txt",
                    timeout=timeout_time)

    gr4 = Graph(input_path + "/input_timeout.txt")
    rez4 = ida_star(gr4, NSOL=NSOL, tip_euristica=euristica,  output_path=output_path + "/output_timeout.txt",
                    timeout=timeout_time)
    print("\nRezultat functie: {}".format(rez1))
    print("\nRezultat functie: {}".format(rez2))
    print("\nRezultat functie: {}".format(rez3))
    print("\nRezultat functie: {}".format(rez4))


def solve(NSOL,input_path,output_path,timeout_time):
    print("Alege un algoritm cu care sa rulezi problema:")
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
        callBF(NSOL,input_path, output_path,timeout_time)
    if s == 2:
        callDF(NSOL, input_path, output_path,timeout_time)
    if s == 3:
        print("Adancimea maxima dorita:", end="")
        adancimeMax = int(input())
        callDFI(NSOL, input_path, output_path,adancimeMax,timeout_time)
    if s == 4:
        callAStar(NSOL,input_path, output_path,timeout_time)
    if s == 5:
        callAStar2(NSOL,input_path, output_path,timeout_time)
    if s == 6:
        callUnif(NSOL,input_path,output_path,timeout_time)

    if s == 7:
       callIdaStar(NSOL,input_path,output_path,timeout_time)





if __name__ == "__main__":
    print("Enter the input folder path:")
    input_path = input()
    print("Enter the output folder path:")
    output_path = input()
    print("Enter the maximum number of solutions:")
    NSOL = int(input())
    print("Enter the timeout time:")
    timeout_time = int(input())


    print("\n\n##################\nSolutii obtinute cu A*:")
    t1 = time.time()

    solve(NSOL,input_path,output_path, timeout_time = timeout_time)

