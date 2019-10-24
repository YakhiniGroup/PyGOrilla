"""
    A http request wrapper providing a python interface for GOrilla.
    Currently output is dumped to an html file. In future should provide a parsed python object.
"""
import os, requests, time, sys, logging
from multiprocessing import freeze_support, Process, Queue
import pandas as pd
from bs4 import BeautifulSoup
from pyGOrilla.HTMLTableParser import HTMLTableParser

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

    def evaluate_list(self, targets, outfilename=None):
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
            logging.info('polling results', end='')
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
                        logging.debug('.', end='')
                        time.sleep(GOrillaEvaluator.sleep_duration)
                else:
                    logging.error(str(response.status_code))
        else:
            logging.error(str(response.status_code))
        logging.info(' elapsed {%s}' % (time.time()-tic))
        return table

    def evaluate_file_folder(self, filein, outfilename=None):
        if os.path.isfile(filein):
            logging.info('Running on single file input')
            try:
                with open(filein, 'r') as f:
                    targets = f.read()
            except:
                logging.error('Failed reading input file!')
            return self.evaluate_list(targets, outfilename)

        elif os.path.exists(sys.argv[1]):
            logging.info('Running on directory with multiple file inputs')
            mypath = filein
            freeze_support()
            q = Queue()
            consumers = []
            num_workers = 4
            for i in range(num_workers):
                consumer = Process(target=self.consume, args=(q, mypath, ))
                consumer.start()
                consumers.append(consumer)

            onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f)) and os.path.splitext(f)[1]=='']

            for tgt in onlyfiles:
                if os.path.exists(os.path.join(mypath, tgt.split('.')[0] + '.GOrilla.html')):
                    continue
                logging.info(tgt)
                q.put(tgt)

            for i in range(num_workers):
                q.put(None)

            for consumer in consumers:
                consumer.join()
        else:
            logging.error('Input not recognized!')

        return None

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
                logging.warning('you are being throttled')
                time.sleep(GOrillaEvaluator.sleep_duration)
        return response


def consume(queue, mypath):
    while True:
        try:
            tgt = queue.get(timeout=30)
            if tgt is None:
                return
            logging.info(tgt)
            with open(os.path.join(mypath, tgt), 'r') as f:
                targets = f.read()

            GOr = GOrillaEvaluator()
            GOr.evaluate_list(targets, os.path.join(mypath, tgt + '.GOrilla.html'))

        except:
            pass


def main():
    if len(sys.argv) == 1:
        logging.error("""Usage options:
                 from pyGOrilla import GOrillaEvaluator
                 GOr = GOrillaEvaluator() # note, this constructor can take parameters
                 restable = GOrillaEvaluator.evaluate_list(genelist, outputfile (optional))
                 GOrillaEvaluator.evaluate_file_folder(inputpath)
                """)
        exit(0)
    else:
        if os.path.exists(sys.argv[1]):
            GOr = GOrillaEvaluator()
            GOr.evaluate_file_folder(sys.argv[1])
    logging.info('Done')


if __name__ == '__main__':
    main()
