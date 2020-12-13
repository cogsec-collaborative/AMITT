''' Manage AMITT counters

Create a page for each of the AMITT counter objects. 
Don't worry about creating notes etc for these - they'll be in the generating spreadsheet
'''

import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import CountVectorizer


class Counter:
    def __init__(self, infile = 'CountersPlaybook_MASTER.xlsx'):
        
        # Load metadata from counters excelfile
        # FIXIT: Ungodly hack = please fix
        xlsx = pd.ExcelFile(infile)
        allamitts = xlsx.parse(['AMITT_objects'])
        dfa = allamitts['AMITT_objects']
        self.dftactics = dfa[3:15].copy()
        self.dfresponses = dfa[18:25].copy()
        self.dfactors = dfa[28:36].copy()
        self.dftechniques = dfa[39:100].copy()

        # Get counters data
        self.dfcounters = pd.read_excel(infile, sheet_name='Countermeasures')
        
        # Create cross-tables
        crossidtechs = self.splitcol(self.dfcounters[['ID', 'Techniques']], 
                                     'Techniques', 'Techs', '\n')
        crossidtechs = crossidtechs[crossidtechs['Techs'].notnull()]
        crossidtechs['TID'] = crossidtechs['Techs'].str.split(' ').str[0]
        crossidtechs.drop('Techs', axis=1, inplace=True)
        self.idtechnique = crossidtechs
        
        crossidres = self.splitcol(self.dfcounters[['ID', 'Resources needed']], 
                                   'Resources needed', 'Res', ',')
        crossidres = crossidres[crossidres['Res'].notnull()]
        self.idresource = crossidres

        
    def analyse_counter_text(self, col='Title'):
        # Analyse text in counter descriptions
        alltext = (' ').join(self.dfcounters[col].to_list()).lower()
        count_vect = CountVectorizer(stop_words='english')
        word_counts = count_vect.fit_transform([alltext])
        dfw = pd.DataFrame(word_counts.A, columns=count_vect.get_feature_names()).transpose()
        dfw.columns = ['count']
        dfw = dfw.sort_values(by='count', ascending=False)
        return(dfw)   

    
    def splitcol(self, df, col, newcol, divider=','):
        # Thanks https://stackoverflow.com/questions/17116814/pandas-how-do-i-split-text-in-a-column-into-multiple-rows?noredirect=1
        return (df.join(df[col]
                        .str.split(divider, expand=True).stack()
                        .reset_index(drop=True,level=1)
                        .rename(newcol)).drop(col, axis=1))

    
    # Print list of counters for each square of the COA matrix
    # Write HTML version of framework diagram to markdown file
    def write_tactics_markdown(self, outfile = '../tactic_counts.md'):

        coacounts = pd.pivot_table(self.dfcounters[['Tactic', 'Response',
                                                    'ID']], index='Response', columns='Tactic', aggfunc=len, fill_value=0)

        html = '''# AMITT Courses of Action matrix:

<table border="1">
<tr>
<td> </td>
'''
        #Table heading = Tactic names
        for col in coacounts.columns.get_level_values(1):
            tid = self.create_tactic_file(col)
            html += '<td><a href="tactics/{0}counters.md">{1}</a></td>\n'.format(
                tid, col)
        html += '</tr><tr>\n'

        # number of counters per response type
        for response, counts in coacounts.iterrows(): 
            html += '<td>{}</td>\n'.format(response)
            for val in counts.values:
                html += '<td>{}</td>\n'.format(val)
            html += '</tr>\n<tr>\n'
        
        # Total per tactic
        html += '<td>TOTALS</td>\n'
        for val in coacounts.sum().values:
                html += '<td>{}</td>\n'.format(val)
        html += '</tr>\n</table>\n'           

        with open(outfile, 'w') as f:
            f.write(html)
            print('updated {}'.format(outfile))
        return

    def create_tactic_file(self, tname):
        if not os.path.exists('../tactics'):
            os.makedirs('../tactics')

        tid = tname[:tname.find(' ')]
        html = '''# Tactic {} counters\n\n'''.format(tname)
        
        html += '## by action\n\n'
        for resp, counters in self.dfcounters[self.dfcounters['Tactic'] == tname].groupby('Response'):
            html += '\n### {}\n'.format(resp)
            
            for c in counters.iterrows():
                html += '* {}: {} (needs {})\n'.format(c[1]['ID'], c[1]['Title'],
                                                    c[1]['Resources needed'])

        html += '\n## by technique\n\n'
        tactecs = self.dftechniques[self.dftechniques['super'] == tid]['Id'].to_list()
        for tech in [tid] + tactecs:
            if tech == tid:
                html += '\n### {}\n'.format(tech)
            else:
                techname = self.dftechniques[self.dftechniques['Id']==tech]['key']
                html += '\n### {}\n'.format(techname)
                
            taccounts = self.idtechnique[self.idtechnique['TID'] == tech]
#            html += '\n{}\n'.format(taccounts)
            for c in self.dfcounters[self.dfcounters['ID'].isin(taccounts['ID'])].iterrows():
                html += '* {}: {} (needs {})\n'.format(c[1]['ID'], c[1]['Title'],
                                                    c[1]['Resources needed'])
        
        datafile = '../tactics/{}counters.md'.format(tid)
        print('Writing {}'.format(datafile))
        with open(datafile, 'w') as f:
            f.write(html)
            f.close()
        return(tid)


    def create_object_file(self, index, rowtype, datadir):

        oid = index
        html = '''# {} counters: {}\n\n'''.format(rowtype, index)

        html += '## by action\n\n'
        for resp, clist in self.dfcounters[self.dfcounters[rowtype] == index].groupby('Response'):
            html += '\n### {}\n'.format(resp)

            for c in clist.iterrows():
                html += '* {}: {} (needs {})\n'.format(c[1]['ID'], c[1]['Title'],
                                                    c[1]['Resources needed'])

        datafile = '{}/{}counters.md'.format(datadir, oid)
        print('Writing {}'.format(datafile))
        with open(datafile, 'w') as f:
            f.write(html)
            f.close()
        return(oid)


    def write_metacounts_markdown(self, outfile = '../metatag_counts.md'):

        coltype = 'Response'
        rowtype = 'metatechnique'
        rowname = 'metatag'
        mtcounts = pd.pivot_table(self.dfcounters[[coltype, rowtype,'ID']], 
                                  index=rowtype, columns=coltype, aggfunc=len, 
                                  fill_value=0) 
        mtcounts['TOTALS'] = mtcounts.sum(axis=1)

        html = '''# AMITT {} courses of action

<table border="1">
<tr>
<td> </td>
    '''.format(rowtype)

        # Table heading row
        for col in mtcounts.columns.get_level_values(1)[:-1]:
            html += '<td>{}</td>\n'.format(col)
        html += '<td>TOTALS</td></tr><tr>\n'

        # Data rows
        datadir = '../{}'.format(rowname)
        if not os.path.exists(datadir):
            os.makedirs(datadir)
        for index, counts in mtcounts.iterrows(): 
            tid = self.create_object_file(index, rowtype, datadir)
            html += '<td><a href="{0}/{1}counters.md">{2}</a></td>\n'.format(
                rowname, tid, index)
            for val in counts.values:
                html += '<td>{}</td>\n'.format(val)
            html += '</tr>\n<tr>\n'

        # Column sums
        html += '<td>TOTALS</td>\n'
        for val in mtcounts.sum().values:
                html += '<td>{}</td>\n'.format(val)
        html += '</tr>\n</table>\n'           

        with open(outfile, 'w') as f:
            f.write(html)
            print('updated {}'.format(outfile))

        return


 
def main():
    counter = Counter()
    counter.write_tactics_markdown()
    counter.write_metacounts_markdown()


if __name__ == "__main__":
    main()
