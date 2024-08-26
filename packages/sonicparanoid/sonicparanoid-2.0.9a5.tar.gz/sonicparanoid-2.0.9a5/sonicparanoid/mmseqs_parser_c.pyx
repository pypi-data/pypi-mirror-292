# -*- coding: utf-8 -*-
"""
This module contains functions to aligment files and compute paralog scores.
"""

from libc.stdio cimport *
from libc.stdlib cimport atoi
# from libc.stdlib cimport atof
import sys
import os
from collections import OrderedDict
import pickle
import gzip



cdef extern from "stdio.h":
    #FILE * fopen ( const char * filename, const char * mode )
    FILE *fopen(const char *, const char *)
    #int fclose ( FILE * stream )
    int fclose(FILE *)
    #ssize_t getline(char **lineptr, size_t *n, FILE *stream);
    ssize_t getline(char **, size_t *, FILE *)



cdef extern from "math.h":
    # minimum
    double fmin  (double x, double y)
    # round to nearest
    double round(double x)



########### FUNCTIONS ############

#write the overlap check in C
cdef inline int check_hsp_overlap_c(int hsp1start, int hsp1end, int hsp2start, int hsp2end):
    """Check hsp overlap (Cython)"""
    if hsp1start == hsp2start: #then there is an overlap for sure
        return 1
    #position the 2 hsp first
    cdef int lxHspStart, lxHspEnd, dxHspStart, dxHspEnd, lenLxHsp, lenDxHsp
    cdef double overlapThr = -0.05
    #position the 2 hsp first
    if hsp1start < hsp2start:
        lxHspStart = hsp1start
        lxHspEnd = hsp1end
        dxHspStart = hsp2start
        dxHspEnd = hsp2end
    else: #tmpS < qstart
        lxHspStart = hsp2start
        lxHspEnd = hsp2end
        #dxHsp = (hsp1[0], hsp1[1])
        dxHspStart = hsp1start
        dxHspEnd = hsp1end
    #calcula the lengths of the HSPs
    lenLxHsp = lxHspEnd - lxHspStart + 1
    lenDxHsp = dxHspEnd - dxHspStart + 1
    #find the shortest HSP
    cdef double shortestHsp = fmin(lenLxHsp, lenDxHsp)
    #calculate the overlap
    cdef double overlap = (dxHspStart - lxHspEnd - 1) / shortestHsp
    #print('Overlap score:\t%s\n'%str(overlap))
    #sys.exit('DEBUG: check_hsp_overlap_c')
    if overlap <= overlapThr:
        #print('Overlap found!')
        return 1
    else: # no overlap
        return 0



def extract_inparanoid_scores_format0_9flds(hspDict, qid: str, sid: str, debug: bool = False) -> tuple[str, str, str, str, str, str, str, str, str]:
    """Extract the scores for an inparanoid graph-node
    Also the overlaps are calculated
    Return a tab-separated string similar to the following:
    63363_O67184 63363_O66911 75.5 564 926 214 303 133 136"""
    if debug:
        print('extract_inparanoid_scores_format0_9flds :: START')
        print('Query:\t{:s}'.format(qid))
        print('Subject:\t{:s}'.format(sid))
        print('Number of HSP:\t{:d}'.format(len(hspDict)))
        #print(hspDict)
    # the meaning of the fileds are the following
    #col1: query
    #col2: subject
    #col3: sum( hsp_i.bitscore )
    #col4: query length [qlen]
    #col5: subject length [slen]
    #col6: max([hsp_1.qend, hsp_2.qend, ... hsp_N.qend]) - min([hsp_1.qstart, hsp_2.qstart, ... hsp_N.qstart] + 1)
    #col7: max([hsp_1.send, hsp_2.send, ... hsp_N.send]) - min([hsp_1.sstart, hsp_2.sstart, ... hsp_N.sstart] + 1)
    #col8: for i=[1, N], sum([hsp_i.qend - hsp_i.qstart] + 1)
    #col9: for i=[1, N], sum([hsp_i.send - hsp_i.sstart] + 1)
    #col10: tab-separated list of all hsp start and end of query subject, in ascending order of the qstart value
    # example of value in col10: q:324-380 h:578-634	q:462-537 h:802-880
    #each entry in the dictionary has qstart for the hsp as key
    #and the following information as values: qlen, slen, qstart, qend, sstart, send, bitscore
    #calculate score in the simple case in which there is only one HS
    # define main variables for HSPS
    cdef int lxHspStart, lxHspEnd, dxHspStart, dxHspEnd, lenLxHsp, lenDxHsp
    cdef int dxQuery, dxHit, lxQuery, lxHit
    cdef int qlen, slen, qstart, qend, sstart, send, bitscore, fBitscore
    cdef int overlapFound, i
    cdef int fCol6, fCol7, fCol8, fCol9
    #cdef double fBitscore
    qFragmentList = [] #contain tuples with start and end positions of hsp on query
    hFragmentList = [] #contain tuples with start and end positions of hsp on hit
    ##tmpDict = {} # will have the qstart as keys and strings like (q:324-380 h:578-634	q:462-537 h:802-880) as values
    if len(hspDict) == 1:
        qlen, slen, qstart, qend, sstart, send, bitscore = list(hspDict.values())[0]
        return(qid, sid, str(bitscore), str(qlen), str(slen), str(qend - qstart + 1), str(send - sstart + 1), str(qend - qstart + 1), str(send - sstart + 1))
        ##return(qid, sid, str(bitscore), str(qlen), str(slen), str(qend - qstart + 1), str(send - sstart + 1), str(qend - qstart + 1), str(send - sstart + 1), ['q:%d-%d h:%d-%d'%(qstart, qend, sstart, send)])
    else:
        fBitscore = 0
        fCol6 = fCol7 = fCol8 = fCol9 = 0
        #these will be used to calculate the overlap
        #and represent the: rightmost end of hsp on query, rightmost end on hsp on hit, leftmost start on hsp on query,  leftmost start on hsp on hit
        dxQuery = dxHit = lxQuery = lxHit = 0
        i = 0
        for hsp in hspDict:
            i = i + 1
            qlen, slen, qstart, qend, sstart, send, bitscore = list(hspDict[hsp])
            if len(qFragmentList) == 0: #then it is the first hsp and must be included in the count
                qFragmentList.append((qstart, qend))
                hFragmentList.append((sstart, send))
                dxQuery = qend
                lxQuery = qstart
                dxHit = send
                lxHit = sstart
                fBitscore = fBitscore + bitscore
                ##tmpDict['%d:%d'%(qstart, qend)] = 'q:%d-%d h:%d-%d'%(qstart, qend, sstart, send)
            else:
                overlapFound = 0 #used to decide if the current hsp should be included in the final score or not
                #check if there is any overlap on the query
                for interval in qFragmentList:
                    #lxHspStart, lxHspEnd, dxHspStart, dxHspEnd, lenLxHsp, lenDxHsp
                    lxHspStart = qstart
                    lxHspEnd = qend
                    dxHspStart = interval[0]
                    dxHspEnd = interval[-1]
                    overlapFound = check_hsp_overlap_c(lxHspStart, lxHspEnd, dxHspStart, dxHspEnd)
                    #overlapFound = check_hsp_overlap((qstart, qend), interval, debug=debug)
                    if overlapFound:
                        #print('Overlap found:\tQUERY')
                        break
                #check if there is any overlap on the hit
                if not overlapFound:
                    for interval in hFragmentList:
                        lxHspStart = sstart
                        lxHspEnd = send
                        dxHspStart = interval[0]
                        dxHspEnd = interval[-1]
                        overlapFound = check_hsp_overlap_c(lxHspStart, lxHspEnd, dxHspStart, dxHspEnd)
                        if overlapFound:
                            #print('Overlap found:\tSUBJECT')
                            break
                #if the overlap was found just skip the hsp
                if overlapFound:
                    continue
                #otherwise include the current hsp
                qFragmentList.append((qstart, qend))
                hFragmentList.append((sstart, send))
                fBitscore += bitscore
                ##tmpDict['%d:%d'%(qstart, qend)] = 'q:%d-%d h:%d-%d'%(qstart, qend, sstart, send)
        #finalize the output record
        #print(bitscore)
        #print(fBitscore)
        #fBitscore = round(fBitscore * 10) / 10
        #print(fBitscore)
        #sys.exit('DEBUG :: multiple hsps')
        ''' # we do not use this information
        #dictionary for strings in col10
        col10Dict = {}
        #insert values in the col10Dict with the qstart as key value (tmpDict dict should not contain same values)
        for k in tmpDict:
            tmpStart = k.split(':')[0]
            col10Dict[int(tmpStart)] = tmpDict[k]
        del tmpDict
        #sort the values for col10
        sorted_list = sorted(col10Dict.items(), key=lambda x: x[0])
        col10List = []
        for el in sorted_list:
            col10List.append(el[1])
        #'''
        #calculate values for column 6, 7, 8, 9
        #load required values for hsp in queries
        tmpStart = []
        tmpEnd = []
        #col8: for i=[1, N], sum([hsp_i.qend - hsp_i.qstart] + 1)
        for el in qFragmentList:
            #print(len(qFragmentList))
            tmpStart.append(el[0])
            tmpEnd.append(el[1])
            fCol8 += el[1] - el[0] + 1
        #col6: max([hsp_1.qend, hsp_2.qend, ... hsp_N.qend]) - min([hsp_1.qstart, hsp_2.qstart, ... hsp_N.qstart]) + 1
        fCol6 = max(tmpEnd) - min(tmpStart) + 1
        #load required values for hsp in subjects
        tmpStart.clear()
        tmpEnd.clear()
        #col9: for i=[1, N], sum([hsp_i.send - hsp_i.sstart] + 1)
        for el in hFragmentList:
            tmpStart.append(el[0])
            tmpEnd.append(el[1])
            fCol9 += el[1] - el[0] + 1
        #col7: max([hsp_1.send, hsp_2.send, ... hsp_N.send]) - min([hsp_1.sstart, hsp_2.sstart, ... hsp_N.sstart] + 1)
        fCol7 = max(tmpEnd) - min(tmpStart) + 1
    #return the required values
    ##return(qid, sid, str(fBitscore), str(qlen), str(slen), str(fCol6), str(fCol7), str(fCol8), str(fCol9), col10List)
    return(qid, sid, str(fBitscore), str(qlen), str(slen), str(fCol6), str(fCol7), str(fCol8), str(fCol9))



def mmseqs_parser_7flds(alignFile, querySeqLenFile, targetSeqLenFile, outDir: str =os.getcwd(), outName: str ="", minBitscore=40, compress:bool=False, complev:int=5, debug=False):
    """
    Parse MMseqs2 results converted to BLAST-like tab-separated files
    The conversion of the MMseqs2 output must be done using convertalis with --format-mode 0, and with some selected columns.
    """
    if debug:
        print("\nmmseqs_parser_7flds :: START")
        print(f"BLAST-formatted file: {alignFile}")
        print(f"Query proteome: {querySeqLenFile}")
        print(f"Target proteome: {targetSeqLenFile}")
        print(f"Outdir: {outDir}")
        print(f"Output name:\t{outName}")
        print(f"Bit-score cutoff below which hits (the sum of the bit-scores) are discarded:\t{minBitscore}")
        print(f"Compress output:\t{compress}")
        if compress:
            print(f"Compression level:\t{complev}")

    # load the dictionaries with sequence lengths
    qidLenDict: dict[str, int] = {}
    with open(querySeqLenFile, "rb") as fd:
      qidLenDict = pickle.load(fd)
    sidLenDict: dict[str, int] = {}
    if querySeqLenFile != targetSeqLenFile:
      #sidLenDict = load_seq_lengths(targetSeqLenFile)
      with open(targetSeqLenFile, "rb") as fd:
        sidLenDict = pickle.load(fd)
    else:
        sidLenDict = qidLenDict

    #create the output directory if does not exist yet
    if outDir != os.getcwd():
        makedir(outDir)
    #name the output file
    cdef str outPath
    if len(outName) == 0:
        sys.stderr.write("ERROR: you must specify a name for the output file resulting from the alignments parsing.")
        sys.exit(-5)
    else:
        outPath = os.path.join(outDir, outName)

    # define file names and file descriptor pointer in C
    filename_byte_string = alignFile.encode("UTF-8")
    cdef char* inputPathC = filename_byte_string
    #file pointers
    cdef FILE* cInputFile
    # varibales for files and lines
    cdef char * ln = NULL
    cdef size_t l = 0
    cdef ssize_t read
    #dictionaries to store results
    currentHitId: tuple[str, str] = ("", "")
    prevHitId: tuple[str, str] = ("", "")
    currentHitDict = OrderedDict()
    #open the output file
    if compress:
        ofd = gzip.open(outPath, "wb", compresslevel=complev)
    else:
        ofd = open(outPath, "w")
    # open alignments file
    cInputFile = fopen(inputPathC, "rb")
    # Set some variables
    cdef int minBitscore_c = <int>minBitscore
    cdef int qlen = 0
    cdef int slen = 0
    cdef int qstart, qend, sstart, send
    cdef int tmpHitScore
    cdef str query_hit_coord
    # NOTE: only for debugging
    '''
    # cdef int wcnt = 0
    # cdef int hspcnt = 0
    '''
    cdef str qid = ""
    cdef str sid = ""
    cdef str outLn = ""
    flds: list[bytes] = []
    hitScore: tuple[str, str, str, str, str, str, str, str, str] = ("", "", "", "", "", "", "", "", "")
    #start reading the output file
    while True:
        ##### Q: query; S: subject; H: hsp
        # Stop reading if it is not the STDOUT stream
        read = getline(&ln, &l, cInputFile)
        if read == -1:
            break
        # hspcnt += 1
        #print(ln)
        # Split to obtain the following fields
        # query,target,qstart,qend,tstart,tend,bits
        # these will be assigned to the following variables
        # qid, sid, qstart, qend, sstart, send, tmpHitScore
        flds = ln.split(b"\t", maxsplit=6)
        # Extract query and target sequence IDs
        qid, sid = [x.decode() for x in flds[:2]]
        # this is to avoid the problem due to the conversion adding _0 or _1 to the subject id...
        # NOTE: This problem was related to early versions of MMSeqs
        # It could now be removed
        ''' # HACK: restore if errors arise
        if qid not in qidLenDict:
            if qid[-2] == "_":
                #print("Query id not found:\t{:s}".format(qid))
                qid = qid[:-2]
                #print("Changed to:\t{:s}".format(qid))
                sys.exit("DEBUG :: query id not found")
        '''
        qlen = qidLenDict[qid]
        # this is to avoid the problem due to the conversion adding _0 or _1 to the subject id...
        # NOTE: This problem was related to early versions of MMSeqs
        # It could now be removed
        ''' # HACK: restore if errors arise
        if sid not in sidLenDict:
            if sid[-2] == "_":
                #print("Target id not found:\t{:s}".format(sid))
                sid = sid[:-2]
                #print("Changed to:\t{:s}".format(sid))
                sys.exit("DEBUG :: target id not found")
        '''
        slen = sidLenDict[sid]
        # extract start and end of the alignment
        qstart = atoi(flds[2]) + 1
        qend = atoi(flds[3])
        query_hit_coord = f"{qstart:d}:{qend:d}"
        sstart = atoi(flds[4]) + 1
        send = atoi(flds[5])
        tmpHitScore = int(flds[6].decode().rstrip("\n"))

        currentHitId = (qid, sid)
        # calculate the hits scores if required
        if currentHitId != prevHitId: #then it is a new hit
            if len(currentHitDict) > 0: #then it is not the first line
                #finalize score caculation
                prevqid, prevsid = prevHitId
                #calculate InParanoid like scores
                hitScore = extract_inparanoid_scores_format0_9flds(currentHitDict, prevqid, prevsid, debug=False)
                #create the final string if the the bitscore for the hit is higher than the cutoff
                if int(hitScore[2]) >= minBitscore_c:
                    outLn = "{:s}\n".format("\t".join(hitScore))
                    if compress:
                        ofd.write(outLn.encode("utf-8"))
                    else:
                        ofd.write(outLn)
                    # wcnt += 1
            currentHitDict.clear() #the ordered dict is better for calculating the overlaps
            #add the hsp to the dictionary
            # currentHitDict["{:d}:{:d}".format(qstart, qend)] = (qlen, slen, qstart, qend, sstart, send, tmpHitScore)
            currentHitDict[query_hit_coord] = (qlen, slen, qstart, qend, sstart, send, tmpHitScore)
            #initialize the scores
            prevHitId = currentHitId
        else: # hsp for the previous hits
            # make sure that the same start and end intervals are not overwritten
            if query_hit_coord not in currentHitDict:
                currentHitDict[query_hit_coord] = (qlen, slen, qstart, qend, sstart, send, tmpHitScore)

    # calculate scores for last hit!
    hitScore = extract_inparanoid_scores_format0_9flds(currentHitDict, qid, sid, debug=False)
    #create the final string if the the bitscore for the hit is higher than the cutoff
    if int(hitScore[2]) >= minBitscore_c:
        outLn = "{:s}\n".format("\t".join(hitScore))
        if compress:
            ofd.write(outLn.encode("utf-8"))
        else:
            ofd.write(outLn)
        # wcnt += 1
    #close input file
    fclose(cInputFile)
    # close the output file
    ofd.close()
    #sys.exit("DEBUG :: mmseqs_parser_7flds")



def dmnd_parser(alignFile, querySeqLenFile, targetSeqLenFile, outDir: str =os.getcwd(), outName: str ="", minBitscore=40, compress:bool=False, complev:int=5, debug=False):
    """
    Parse Diamond results in BLAST-like tab-separated files with 7 filed
    The output format is obtained using the following command (since Diamond ver 2) '-f 6 qseqid sseqid qstart qend sstart send bitscore'.
    """
    if debug:
        print("\ndmnd_parser :: START")
        print(f"BLAST-formatted file: {alignFile}")
        print(f"Query proteome: {querySeqLenFile}")
        print(f"Target proteome: {targetSeqLenFile}")
        print(f"Outdir: {outDir}")
        print(f"Output name:\t{outName}")
        print(f"Bit-score cutoff below which hits (the sum of the bit-scores) are discarded:\t{minBitscore}")
        print(f"Compress output:\t{compress}")
        if compress:
            print(f"Compression level:\t{complev}")

    # load the dictionaries with sequence lengths
    #qidLenDict = load_seq_lengths(querySeqLenFile)
    # Use pickles instead
    qidLenDict: dict[str, int] = {}
    with open(querySeqLenFile, "rb") as fd:
      qidLenDict = pickle.load(fd)
    sidLenDict: dict[str, int] = {}
    if querySeqLenFile != targetSeqLenFile:
      #sidLenDict = load_seq_lengths(targetSeqLenFile)
      with open(targetSeqLenFile, "rb") as fd:
        sidLenDict = pickle.load(fd)
    else:
        sidLenDict = qidLenDict

    #create the output directory if does not exist yet
    if outDir != os.getcwd():
        makedir(outDir)
    #name the output file
    cdef str outPath
    if len(outName) == 0:
        sys.stderr.write("ERROR: you must specify a name for the output file resulting from the alignments parsing.")
        sys.exit(-5)
    else:
        outPath = os.path.join(outDir, outName)

    # define file names and file descriptor pointer in C
    filename_byte_string = alignFile.encode("UTF-8")
    cdef char* inputPathC = filename_byte_string
    #file pointers
    cdef FILE* cInputFile
    # varibales for files and lines
    cdef char * ln = NULL
    cdef size_t l = 0
    cdef ssize_t read
    #dictionaries to store results
    currentHitId: tuple[str, str] = ("", "")
    prevHitId: tuple[str, str] = ("", "")
    currentHitDict = OrderedDict()
    #open the output file
    if compress:
        ofd = gzip.open(outPath, "wb", compresslevel=complev)
    else:
        ofd = open(outPath, "w")
    # open alignments file
    cInputFile = fopen(inputPathC, "rb")
    cdef int minBitscore_c = <int>minBitscore
    # set some variables
    cdef int qlen = 0
    cdef int slen = 0
    cdef int qstart, qend, sstart, send
    cdef int tmpHitScore
    cdef str query_hit_coord
    ''' NOTE: only for debugging
    # cdef int wcnt = 0
    # cdef int hspcnt = 0
    '''
    cdef str qid = ""
    cdef str sid = ""
    cdef str outLn = ""
    flds: list[bytes] = []
    hitScore: tuple[str, str, str, str, str, str, str, str, str] = ("", "", "", "", "", "", "", "", "")
    #start reading the output file
    while True:
        ##### Q: query; S: subject; H: hsp
        # Stop reading if it is not the STDOUT stream
        read = getline(&ln, &l, cInputFile)
        if read == -1:
            break
        # hspcnt += 1
        #print(ln)
        # Split to obtain the following fields
        # qseqid,sseqid,qstart,qend,sstart,send,bitscore
        # these will be assigned to the following variables
        # qid, sid, qstart, qend, sstart, send, tmpHitScore
        flds = ln.split(b"\t", maxsplit=6)
        # Extract query and target sequence IDs
        qid, sid = [x.decode() for x in flds[:2]]
        qlen = qidLenDict[qid]
        slen = sidLenDict[sid]
        # extract start and end of the alignment
        qstart = atoi(flds[2]) + 1
        qend = atoi(flds[3])
        query_hit_coord = f"{qstart}:{qend}"
        sstart = atoi(flds[4]) + 1
        send = atoi(flds[5])
        # In Diamond the bitscore is float so it need to be rounded
        # to the closest integer
        # TODO: the check tmpHitScore >= minBitscore_c should be
        # perfomed in advance to avoid score with low hits to be added
        # to the dictionary with hits
        tmpHitScore = int(round(float(flds[6].decode().rstrip("\n"))))
        # HACK: tmpHitScore >= minBitscore_c before HSPs are added to dictionary
        # This should avoid the predictions from multiple low-score HSPs
        if tmpHitScore >= minBitscore_c:
            currentHitId = (qid, sid)
            # calculate the hits scores if required
            if currentHitId != prevHitId: #then it is a new hit
                if len(currentHitDict) > 0: #then it is not the first line
                    #finalize score caculation
                    prevqid, prevsid = prevHitId
                    #calculate InParanoid like scores
                    hitScore = extract_inparanoid_scores_format0_9flds(currentHitDict, prevqid, prevsid, debug=False)
                    #create the final string if the the bitscore for the hit is higher than the cutoff
                    if int(hitScore[2]) >= minBitscore_c:
                        outLn = "{:s}\n".format("\t".join(hitScore))
                        if compress:
                            ofd.write(outLn.encode("utf-8"))
                        else:
                            ofd.write(outLn)
                        # wcnt += 1
                currentHitDict.clear() #the ordered dict is better for calculating the overlaps
                #add the hsp to the dictionary
                currentHitDict[query_hit_coord] = (qlen, slen, qstart, qend, sstart, send, tmpHitScore)
                #initialize the scores
                prevHitId = currentHitId
            else: #hsp for the previous hits
                # make sure that the same start and end intervals are not overwritten
                if query_hit_coord not in currentHitDict:
                    currentHitDict[query_hit_coord] = (qlen, slen, qstart, qend, sstart, send, tmpHitScore)
    # calculate scores for last hit!
    hitScore = extract_inparanoid_scores_format0_9flds(currentHitDict, qid, sid, debug=False)
    #create the final string if the the bitscore for the hit is higher than the cutoff
    if int(hitScore[2]) >= minBitscore_c:
        outLn = "{:s}\n".format("\t".join(hitScore))
        if compress:
            ofd.write(outLn.encode("utf-8"))
        else:
            ofd.write(outLn)
        # wcnt += 1
    #close input file
    fclose(cInputFile)
    # close the output file
    ofd.close()



def makedir(path):
    """Create a directory including the intermediate directories in the path if not existing."""
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
