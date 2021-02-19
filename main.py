# SERBOI FLOREA-DAN 335CB

# importam acest modul pentru acces la parametri dati din linia de comanda
import sys

# extrag informatiile legate de NFA din fisierul de input
def read_NFA():
    # deschid fisierul de input
    in_file = open(in_filename, "r")
    # citesc numarul de stari al NFA-ului
    no_states = int(in_file.readline().split()[0])
    # citesc starile finale ale NFA-ului
    final_states = in_file.readline().split()
    # memorez alfabetul NFA-ului
    symbols = set()
    # calculez multimea starilor
    states_set = set()
    # citesc tranzitiile NFA-ului
    NFA_trans = {}
    for line in in_file:
        # citesc tranzitia din fisier
        line_transition = line.split()
        # adaug simbolul in set
        symbols.add(line_transition[1])
        # adaug tranzitia in dictionarul cu tranzitii, 
        # cheia fiind starea de unde se face tranzitia
        # iar valoarea fiind o lista de perechi (simbol, lista stari urmatoare)
        curr_state_trans = NFA_trans.get(line_transition[0], [])
        curr_state_trans.append((line_transition[1], line_transition[2:]))
        NFA_trans[line_transition[0]] = curr_state_trans
        # actualizez multimea starilor
        states_set.add(line_transition[0])
        for s in line_transition[2:]:
            states_set.add(s)
    # inchid fisierul de input
    in_file.close()
    return no_states, final_states, symbols, states_set, NFA_trans

# functia calculeaza inchiderea epsilon pentru o stare
def eps_closure(state, NFA_trans):
    handled_states = set()
    unhandled_states = set()
    unhandled_states.add(state)
    while len(unhandled_states) > 0:
        curr_state = unhandled_states.pop()
        handled_states.add(curr_state)
        curr_state_trans = NFA_trans.get(curr_state, [])
        for symbol, next_states in curr_state_trans:
            if symbol == 'eps':
                for next_state in next_states:
                    if next_state not in handled_states:
                        unhandled_states.add(next_state)
    return handled_states

# functia concateaza o multime de stari sub forma unui string
# starile fiind delimitate prin '/'
def compute_composed_state(states):
    composed_state = ""
    sorted_states = sorted(states)
    for i in range(len(sorted_states)):
        if i != 0:
            composed_state += '/'
        composed_state += sorted_states[i]
    return composed_state

# functia construieste DFA-ul
def compute_DFA(final_states, NFA_trans):
    # construim starea initiala a DFA-ului
    # care reprezinta inchiderea epsilon a starii initiale din NFA
    # o memoram ca string, concatenand starile, delimitate prin '/'
    init_state_eps_closure = eps_closure('0', NFA_trans)
    DFA_initial_state = compute_composed_state(init_state_eps_closure)
    DFA_trans = {}
    DFA_final_states = set()
    # vom tine in memorie multimea starilor neprelucrate si a celor prelucrate
    unhandled_states = set()
    handled_states = set()
    # vom porni de la starea initiala
    unhandled_states.add(DFA_initial_state)
    # cat timp avem stari neprelucrate
    while(len(unhandled_states) > 0):
        # extragem o stare neprelucrata, construim tranzitiile in DFA
        composed_state = unhandled_states.pop()
        handled_states.add(composed_state)
        composed_state_list = str(composed_state).split('/')
        # starea compusa este stare finala in DFA
        # daca cel putin o stare continuta este stare finala in NFA
        for s in composed_state_list:
            if s in final_states:
                DFA_final_states.add(composed_state)
        # calculam tranzitiile pentru aceasta stare compusa
        trans = {}
        for curr_state in composed_state_list:
            curr_state_trans = NFA_trans.get(curr_state, [])
            # parcurgem tranzitiile starii curente din multimea starii compuse
            for symbol, next_states in curr_state_trans:
                if symbol != 'eps':
                    t = trans.get(symbol, [])
                    # adaugam starile urmatoare in multimea starilor urmatoare 
                    # pentru starea compusa curenta
                    for n_st in next_states:
                        t.append(n_st)
                        n_st_closure = eps_closure(n_st, NFA_trans)
                        t[0:0] = n_st_closure
                    trans[symbol] = list(set(t))
        # inlocuim multimile starilor urmatoare 
        # cu reprezentarea lor concatenata ca string
        for symbol in trans.keys():
            value = trans.get(symbol, [])
            new_composed_state = compute_composed_state(value)
            trans[symbol] = new_composed_state
            # daca starea noua compusa nu se afla printre cele tratate
            if new_composed_state not in handled_states:
                # adaugam starea in multimea celor netratate
                unhandled_states.add(new_composed_state)
        # completam tabelul de tranzitii pentru starea compusa curenta
        DFA_trans[composed_state] = trans
    return DFA_final_states, DFA_trans

# functia scrie in fisier starile finale ale DFA-ului
def write_final_states(out_file, DFA_final_states, states_map):
    first = 1
    for final_state in DFA_final_states:
        if first == 1:
            first = 0
            out_file.write(states_map[final_state])
        else:
            out_file.write(' ' + states_map[final_state])
    out_file.write('\n')

# functia scrie in fisier tranzitiile DFA-ului
def write_transitions(out_file, DFA_trans, states_map, symbols, curr_no):
    for state in DFA_trans.keys():
        transition = DFA_trans[state]
        for symbol in symbols:
            out_file.write(states_map[state] + ' ')
            n_st = transition.get(symbol, '-1')
            # verificam daca exista tranzitie pe simbolul curent
            if n_st != '-1':
                out_file.write(symbol + ' ' + states_map[n_st])
            # altfel, ajungem in sink state
            else:
                out_file.write(symbol + ' ' + str(curr_no))
            out_file.write('\n')
    # tranzitiile pentru sink state
    for symbol in symbols:
        out_file.write(str(curr_no) + ' ' + symbol + ' ' + str(curr_no) + '\n')

# scriu informatiile legate de DFA in fisierul de output
def write_DFA():
    # deschid fisierul de output
    out_file = open(out_filename, "w")
    # scriu in fisier numarul de stari pentru DFA
    # la care se mai adauga starea sink care va fi construita ulterior
    out_file.write(str(len(DFA_trans.keys()) + 1) + '\n')
    # mapez starile obtinute la intregi
    curr_no = 0
    states_map = {}
    for state in DFA_trans.keys():
        states_map[state] = str(curr_no)
        curr_no = curr_no + 1
    # scriu starile finale in fisier
    write_final_states(out_file, DFA_final_states, states_map)
    # nu avem tranzitii pe simbolul epsilon intr-un DFA
    if 'eps' in symbols:
        symbols.remove('eps')
    # scriu tranzitiile DFA-ului
    write_transitions(out_file, DFA_trans, states_map, symbols, curr_no)
    # inchid fisierul de output
    out_file.close()

if __name__ == '__main__':

    # extrag denumirile fisierelor de input si output date din linia de comanda
    in_filename = sys.argv[1]
    out_filename = sys.argv[2]

    # extrag numarul de stari, starile finale, simbolurile, multimea starilor
    # si tranzitiile NFA-ului din fisierul de input
    no_states, final_states, symbols, states_set, NFA_trans = read_NFA()

    # calculez inchiderea epsilon pentru fiecare stare a NFA-ului
    eps_closure_all_states = {}
    for st in NFA_trans.keys():
        eps_closure_all_states[st] = eps_closure(st, NFA_trans)
    
    # calculez DFA-ul
    DFA_final_states, DFA_trans = compute_DFA(final_states, NFA_trans)

    # scriu numarul de stari, starile finale si tranzitiile DFA-ului
    # in fisierul de ouput
    write_DFA()