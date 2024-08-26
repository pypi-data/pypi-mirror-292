# -*- coding: utf-8 -*-
"""
This module contains functions that perform ID mapping on ortholog tables.
"""

from libc.stdio cimport *
cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)
    int fclose(FILE *)
    ssize_t getline(char **, size_t *, FILE *)

import sys
import os
import pickle
import queue
import multiprocessing as mp

### Worker functions (1 cpu) ###
# def consume_remap_pairwise_relations(jobs_queue, results_queue, inTblRoot:str, outTblRoot:str,  new2OldHdrAllSp: dict[str, dict[str, str]], mergedTables: bool) -> None:
cdef void consume_remap_pairwise_relations(object jobs_queue, object results_queue, str inTblRoot, str outTblRoot, dict new2OldHdrAllSp, bint mergedTables):
    """Remap pairsire relation using 1 cpu."""

    cdef str A
    cdef str B
    cdef str inTbl
    cdef str outTbl
    cdef str tblType

    # jobs_queue contains tuples with input and output paths
    while True:
        try:
            current_input = jobs_queue.get(True, 1)
            if current_input is None:
                break
            A, B = current_input[0]
            # Set a different name depending if the table is merged with arch-based predictions
            # or only contains graph-based ones
            if mergedTables:
                tblType = "mtable"
            else:
                tblType = "table"

            inTbl = os.path.join(inTblRoot, f"{A}/{tblType}.{A}-{B}")
            remappedA, remappedB = current_input[1]
            outTbl = os.path.join(outTblRoot, f"{remappedA}/{remappedA}-{remappedB}")
            makedir(os.path.dirname(outTbl))
            # remap pairwise relations
            if A == B:
                remap_pairwise_relations(inTbl, outTbl, new2OldHdrAllSp[A], new2OldHdrAllSp[A], write_aln_scores=0, debug=0)
            else:
                remap_pairwise_relations(inTbl, outTbl, new2OldHdrAllSp[A], new2OldHdrAllSp[B], write_aln_scores=0, debug=0)
            # add the computed pair
            results_queue.put((f"{A}-{B}", f"{remappedA}-{remappedB}"))
            # sys.exit("DEBUG@remap_tables_c.pyx -> consume_remap_pairwise_relations")
        except queue.Empty:
            print("WARNING: consume_remap_pairwise_relations -> Queue found empty when it actually is not...\nNothing to worry about it. We will try again to get a valid value from the queue.")



### Job processing Functions
def remap_pairwise_relations_parallel(pairsFile, runDir=os.getcwd(), orthoDbDir=os.getcwd(), mergedTables: bool = False, threads=4, debug=False) -> None:
    """Remap pairwise ortholog relations in parallel."""
    auxDir: str = os.path.join(runDir, "aux")
    inputSeqInfoDir: str = os.path.join(auxDir, "input_seq_info")
    if debug:
        print("\nremap_pairwise_relations_parallel :: START")
        print(f"File with pairs to be mapped: {pairsFile}")
        print(f"Run directory: {runDir}")
        print(f"Directory with auxiliary files: {auxDir}")
        print(f"Directory with ortholog relations to be mapped: {orthoDbDir}")
        print(f"Merged graph- and arch-based predictions:\t{mergedTables}")
        print(f"Threads:\t{threads}")
    # get input files paths
    A: str = ""
    B: str = ""
    cdef unsigned int tblCnt = 0
    cdef unsigned int spCnt = 0
    tmpTpl: tuple[str, str] = ("", "") 
    # load all mapping dictionaries
    cdef dict new2OldHdrAllSp = {} # dict[str, dict[str, str]]
    cdef dict id2SpDict = {} # dict[str, str]
    # File with species mapping info
    cdef str speciesFile = os.path.join(auxDir, "species.tsv")
    # output directory for remapped tables
    cdef str remapOutDir = os.path.join(runDir, "species_to_species_orthologs/")

    # load the species IDs mapping
    for ln in open(speciesFile, "rt"):
      mapId, spName, d1 = ln.split("\t", 2)
      spCnt += 1
      if not mapId in id2SpDict:
        id2SpDict[mapId] = spName

    # create the queue and start adding
    cdef unsigned int combinations = int(spCnt * ((spCnt - 1) / 2))
    remap_queue = mp.Queue(maxsize=combinations + threads)

    # fill the queue with tuples containing the original and remapped species names
    # EXAMPLE: (A, B) and mapped species names (remap(A), remap(B))
    # and load the pickle files
    for pair in open(pairsFile, "r"):
      A, B = pair[:-1].split("-", 1)
      tblCnt += 1
      sys.stdout.flush()
      # load the mapping dictionaries if necessary
      if A not in new2OldHdrAllSp:
        # load the pickle
        tmpPickle = os.path.join(inputSeqInfoDir, f"hdr_{A}.pckl")
        with open(tmpPickle, "br") as fd:
          new2OldHdrAllSp[A] = pickle.load(fd)
      # now do the same thing for B
      if B not in new2OldHdrAllSp:
        # load the pickle
        tmpPickle = os.path.join(inputSeqInfoDir, f"hdr_{B}.pckl")
        with open(tmpPickle, "br") as fd:
          new2OldHdrAllSp[B] = pickle.load(fd)
      # Add Tuples with Tuples of input Species IDs (A, B) and mapped species names (remap(A), remap(B))
      remap_queue.put(((A, B), (id2SpDict[A], id2SpDict[B])))
    if debug:
      print(f"Input species:\t{spCnt}")
      print(f"Pairwise tables to be remapped:\t{combinations}")

    # add flags for completed jobs
    for i in range(0, threads):
        sys.stdout.flush()
        remap_queue.put(None)
    # Queue to contain the execution time
    results_queue = mp.Queue(maxsize=combinations)

    # call the method inside workers
    cdef list runningJobs = [mp.Process(target=consume_remap_pairwise_relations, args=(remap_queue, results_queue, orthoDbDir, remapOutDir, new2OldHdrAllSp, mergedTables)) for i_ in range(threads)]

    for proc in runningJobs:
        proc.start()

    while True:
        try:
            rawPair, remapPair = results_queue.get(False, 0.01)
            # if debug:
            #   sys.stdout.write(f"Remapping done for:\t{rawPair} -> {remapPair}\n")
        except queue.Empty:
            if debug:
                print("INFO: remap_pairwise_relations_parallel -> processed all the results in queue...\n")

        allExited = True
        for t in runningJobs:
            if t.exitcode is None:
                allExited = False
                break
        if allExited & results_queue.empty():
            break

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()
    # sys.exit("DEBUG@remap_tables_c.pyx -> remap_pairwise_relations_parallel")



#### Other functions ####

# def remap_pairwise_relations(inTbl: str, outTbl: str, old2NewHdrDictA: dict[str, str], old2NewHdrDictB: dict[str, str], debug=False) -> None:
cdef void remap_pairwise_relations(str inTbl, str outTbl, dict old2NewHdrDictA, dict old2NewHdrDictB, bint write_aln_scores=0, bint debug=0):
    """Read a table with pairwise relations and add the original FASTA header."""
    if debug:
        print(f"\nremap_pairwise_relations (Cython) :: START")
        print(f"Input table: {inTbl}")
        print(f"Output table: {outTbl}")
        print(f"Headers to remap for species A:\t{len(old2NewHdrDictA)}")
        print(f"Headers to remap for species B:\t{len(old2NewHdrDictB)}")
        print(f"Write alignment scores:\t{write_aln_scores}")
    if not os.path.isfile(inTbl):
        sys.stderr.write(f"\nThe file {inTbl} was not found,\nplease provide a valid input path.\n")
        sys.exit(-2)

    # The tables have a different for layouts depending if these are graph-based only or also contain domain-based orthologs

    # Graph-based tables look as follow and have names linke table.sp1-sp2
    # OrtoId\tScore\tOrthoA\tOrthoB
    # 14\t620\t1.49 1.0\t3.1653 1.0 3.373 0.385

    # Tables which also contain domain-based orthologs (aka merged tables) look as follow and have names linke mtable.sp1-sp2
    # Size\tRelations\tOrthoA\tOrthoB
    # 2\t1\t2.1126 1\t4.1790 1

    # define the variables
    cdef int rdCnt = 0
    cdef int wrtCnt = 0
    cdef bint graph_only = 0
    # Graph only table file names have follow the naming pattern "table.A-B"
    if os.path.basename(inTbl)[0] == "t":
        graph_only = 1

    # define file names and file descriptor pointer in C
    filename_byte_string = inTbl.encode("UTF-8")
    cdef char* inTbl_c = filename_byte_string
    #file pointer
    cdef FILE* cfile
    # varibales for files and lines
    cdef char * line = NULL
    cdef size_t l = 0
    cdef ssize_t read
    cdef str clstrId = ""
    cdef str clstrSc = ""
    # Number of proteins in the cluster
    cdef int clstrSize = 0
    # Number of 1-to-1 relations
    cdef int relCnt = 0
    cdef str clstrLx = "" # part from species A
    cdef str clstrRx = "" # part from species B
    cdef str newClstr = "" # remapped string
    cdef str tmpStrRx = ""
    cdef str tmpStrLx = ""
    # list to be used during the split
    cdef list tmpListLx = [] # list[str]
    cdef list tmpListRx = [] # list[str]
    cdef float tmpListLxLen = 0
    cdef float tmpListRxLen = 0
    cdef list flds # list[bytes]

    #open the pairwise ortholog table
    cfile = fopen(inTbl_c, "rb")
    if cfile == NULL:
        raise FileNotFoundError(2, f"No such file or directory: '{inTbl_c}'" )

    # open the output file
    ofd = open(outTbl, "wt")
    # read the file, remap the ids and write in the new output table
    while True:
        read = getline(&line, &l, cfile)
        if read == -1:
            break
        rdCnt += 1

        # if the last letter is a 'B' then it is the cluster headers
        if line.decode()[-2] == "B":
            if (not graph_only) or (graph_only and write_aln_scores):
                ofd.write(line.decode())
            else:
                # This means that it is graph_only=1 and that write_aln_scores=0
                ofd.write("Size\tRelations\tOrthoA\tOrthoB\n")
            wrtCnt += 1
            continue
        # split the cluster string
        flds = line.split(b'\t', 3)
        clstrId = flds[0].decode()
        clstrSc = flds[1].decode()
        clstrLx = flds[2].decode()
        clstrRx = flds[3].decode().rstrip("\n")

        # map elements of the left part of the cluster
        # example: 3.1653 1.0 3.373 0.385 -> gene1 1.0 gene2 0.385
        tmpListLx = clstrLx.split(" ")
        for i, val in enumerate(tmpListLx):
            if i % 2 == 0: # then we map the FASTA header
                tmpListLx[i] = old2NewHdrDictA[val]
            elif graph_only: # graph-only tables have 1.0 instead of 1 for seed orthologs
                if val[0] == "1":
                    tmpListLx[i] = "1"

        # map elements of the right part of the cluster
        tmpListRx = clstrRx.split(" ")
        for i, val in enumerate(tmpListRx):
            if i % 2 == 0: # then we map the FASTA header
                tmpListRx[i] = old2NewHdrDictB[val]
            elif graph_only: # graph-only tables have 1.0 instead of 1 for seed orthologs
                if val[0] == "1":
                    tmpListRx[i] = "1"

        # ofd.write("{:s}\t{:s}\t{:s}\t{:s}".format(clstrId, clstrSc, " ".join(tmpListLx), " ".join(tmpListRx)))
        tmpStrLx = " ".join(tmpListLx)
        tmpStrRx = " ".join(tmpListRx)

        # NOTE: In this part we might need to compute the cluster size and number of relations
        # depending on the values of graph_only and weite_aln_scores
        if (not graph_only) or (graph_only and write_aln_scores):
            ofd.write(f"{clstrId}\t{clstrSc}\t{tmpStrLx}\t{tmpStrRx}\n")
        else:
            # print("Write graph-based table including cluster sizes and 1-to-1 relation counts...")
            tmpListLxLen = len(tmpListLx)/2.0
            tmpListRxLen = len(tmpListRx)/2.0
            clstrSize = int(tmpListRxLen + tmpListLxLen)
            relCnt = int(tmpListRxLen * tmpListLxLen)
            ofd.write(f"{clstrSize}\t{relCnt}\t{tmpStrLx}\t{tmpStrRx}\n")

        wrtCnt += 1

    #close input file
    fclose(cfile)
    # sys.exit("DEBUG@remap_tables_c.pyx -> remap_pairwise_relations")


def makedir(path):
    """Create a directory including the intermediate directories in the path if not existing."""
    # check the file or dir does not already exist
    if os.path.isfile(path):
        sys.stderr.write(f"\nWARNING: {path}\nalready exists as a file, and the directory cannot be created.\n")
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
