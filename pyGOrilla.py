"""
    A http request wrapper providing a python interface for GOrilla.
    Currently output is dumped to an html file. In future should provide a parsed python object.
"""
import os, requests, time, sys
from multiprocessing import freeze_support, Process, Queue
import pandas as pd
from bs4 import BeautifulSoup

from HTMLTableParser import HTMLTableParser
done = False

class GOrillaEvaluator:
    parameters = {"application": "gorilla", "run_mode": "mhg", "species": "HOMO_SAPIENS", "db": "proc",
                  "pvalue_thresh": "0.001", "analysis_name": "",
                  "user_email": "", "fast_mode": "on"}
    sleep_duration = 5

    def __init__(self, override_params=None):
        """

        :param override_params: a dictionary of string parameters to pass to GOrilla webserver.
        e.g. {"species": "MUS_MUSCULUS"} to change species list.
        {"db": "all"} to change GO from process to process/function/component.
        """
        if override_params is not None:
            for k, v in override_params:
                self.parameters[k] = v

    def evaluate(self, targets, outfilename=None):
        """

        :param targets: input list of gene names
        :param outfilename: output filename to save the resulting html file
        :return: returns a pandas dataframe with a parsed table of the enrichment results
        """
        self.parameters["target_set"] = targets
        tic = time.time()
        response = GOrillaEvaluator._auto_retry('http://cbl-gorilla.cs.technion.ac.il/servlet/GOrilla', self.parameters)
        table = None
        poll_done = False
        if response.status_code == 200:
            print('polling results', end='')
            while not poll_done:
                response2 = GOrillaEvaluator._auto_retry(response.url)
                if response2.status_code == 200:
                    if "<title>Calculating Enrichment</title>" not in response2.text:
                        poll_done = True
                        if outfilename is not None:
                            with open(outfilename, "wb") as myfile:
                                myfile.write(response2.content)
                        soup = BeautifulSoup(response2.content, 'html.parser')
                        tbls = soup.find_all('table')
                        if len(tbls) > 1:
                            table = HTMLTableParser.parse(tbls[1])
                            table.columns = [v.strip() for v in table.iloc[0]]
                            table = table.drop(index=0)
                            table.set_index("GO term")

                    else:
                        print('.', end='')
                        time.sleep(GOrillaEvaluator.sleep_duration)
                else:
                    print('error:' + str(response.status_code))
        else:
            print('error:' + str(response.status_code))
        print(' elapsed {%s}' % (time.time()-tic))
        return table

    @staticmethod
    def _auto_retry(uri, parameters=None):
        requesting = True
        while requesting:
            try:
                if parameters is None:
                    response = requests.get(uri)
                else:
                    response = requests.post(uri, files=parameters)
                requesting = False
            except requests.exceptions.ConnectionError:
                print('you are being throttled')
                time.sleep(GOrillaEvaluator.sleep_duration)
        return response


def consume(queue, mypath):
    while not done:
        try:
            tgt = queue.get(timeout=30)
            if tgt is None:
                return
            print(tgt)
            with open(os.path.join(mypath, tgt), 'r') as f:
                targets = f.read()

            GOr = GOrillaEvaluator()
            GOr.evaluate(targets, os.path.join(mypath, tgt + '.GOrilla.html'))

        except:
            pass


def main():
    if len(sys.argv) == 1:
        print("""Usage options:
                 1. python pyGOrilla.py <input filename>
                 Such that <input file> contains sorted list of gene names.
                 2. python pyGOrilla.py <input folder>
                 Such that <input folder> contains multiple files with sorted list of gene names, where the files have a blank file extention (e.g. "filename.").
                 3. In python code: 
                 from pyGOrilla import GOrillaEvaluator
                 GOr = GOrillaEvaluator() # note, this constructor can take parameters
                 GOrillaEvaluator.evaluate(genelist, outputfile)
                """)
        exit(0)
    else:
        if os.path.isfile(sys.argv[1]):
            print('Running on single file input')
            try:
                with open(sys.argv[1], 'r') as f:
                    targets = f.read()
            except:
                print('Failed reading input file!')
            GOr = GOrillaEvaluator()
            GOr.evaluate(targets, sys.argv[1] + ".GOrilla.html")

        elif os.path.exists(sys.argv[1]):
            print('Running on directory with multiple file inputs')
            mypath = sys.argv[1]
            freeze_support()
            q = Queue()
            consumers = []
            num_workers = 4
            for i in range(num_workers):
                consumer = Process(target=consume, args=(q, mypath, ))
                consumer.start()
                consumers.append(consumer)

            onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f)) and os.path.splitext(f)[1]=='']

            for tgt in onlyfiles:
                if os.path.exists(os.path.join(mypath, tgt.split('.')[0] + '.GOrilla.html')):
                    continue
                print(tgt)
                q.put(tgt)

            for i in range(num_workers):
                q.put(None)

            for consumer in consumers:
                consumer.join()
        else:
            print('Input not recognized!')
    print('Done')


if __name__ == '__main__':
    main()
