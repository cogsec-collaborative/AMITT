''' Manage AMITT metadata

The AMITT github repo at https://github.com/cogsec-collaborative/AMITT serves multiple purposes:
* Holds the master copy of AMITT (in excel file AMITT_TTPs_MASTER.xlsx)
* Holds detailed notes on each phase, tactic, technique, incident, task and counter in
  AMITT.  These notes are markdown pages that people are free to suggest edits to, using git's 
  fork mechanisms. 
* Holds a list of suggested changes to AMITT, in the github repo's issues list
* Provides a set of indexed views of AMITT objects, to make exploring AMITT easier

The file in this code updates the github repo contents, after the master spreadsheet is updated. 
It creates this: 
* A html page for each AMITT TTP object (creator and counter), if it doesn't already exist.  
  If a html page does exist, update the metadata on it, and preserve any hand-created 
  notes below the metadata area in it.
* A html page for each AMITT phase, tactic, and task.
* A html page for each incident used to create AMITT
* A grid view of all the AMITT creator techniques
* A grid view of all the AMITT counter techniques
* Indexes for the counter techniques, by tactic, resource and metatag

Here are the file inputs and outputs associated with that work: 

Reads 1 excel file: ../AMITT_MASTER_DATA/AMITT_TTPs_MASTER.xlsx with sheets: 
* phases
* techniques
* tasks
* incidents
* incidenttechniques
* tactics
* countermeasures
* actortypes
* resources
* responsetypes

Reads template files:
* template_phase.md
* template_tactic.md
* template_task.md
* template_technique.md
* template_incident.md
* template_counter.md

Creates markdown files: 
* ../amitt_blue_framework.md
* ../amitt_red_framework.md
* ../amitt_red_framework_clickable.md
* ../incidents_list.md
* ../counter_tactic_counts.md
* ../metatechniques_by_responsetype.md
* ../resources_by_responsetype.md
* ../tactics_by_responsetype.md
* ../counter_tactics/*counters.md
* ../metatechniques/*.md
* ../resources_needed/*.md

Updates markdown files:
* ../phases/*.md
* ../tactics/*.md
* ../techniques/*.md
* ../incidents/*.md
* ../tasks/*.md
* ../counters/*.md

Creates CSVs
* ../generated_csvs/counters_tactics_table.csv
* ../generated_csvs/techniques_tactics_table.csv

todo: 
* add all framework comments to the repo issues list
'''

import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import CountVectorizer


class Amitt:

    
    def __init__(self, infile = '../AMITT_MASTER_DATA/AMITT_TTPs_MASTER.xlsx'):
        
        # Load metadata from file
        metadata = {}
        xlsx = pd.ExcelFile(infile)
        for sheetname in xlsx.sheet_names:
            metadata[sheetname] = xlsx.parse(sheetname)
            metadata[sheetname].fillna('', inplace=True)

        # Create individual tables and dictionaries
        self.df_phases = metadata['phases']
        self.df_techniques = metadata['techniques']
        self.df_tasks = metadata['tasks']
        self.df_incidents = metadata['incidents']
        self.df_counters = metadata['countermeasures'].sort_values('id')
        self.df_counters[['tactic_id', 'tactic_name']] = self.df_counters['tactic'].str.split(' ', 1, expand=True)
        self.df_counters[['metatechnique_id', 'metatechnique_name']] = self.df_counters['metatechnique'].str.split(' ', 1, expand=True)
        self.df_detections = metadata['detections']
        self.df_detections[['tactic_id', 'tactic_name']] = self.df_detections['tactic'].str.split(' ', 1, expand=True)
#        self.df_detections[['metatechnique_id', 'metatechnique_name']] = self.df_detections['metatechnique'].str.split(' ', 1, expand=True)
        self.df_actortypes = metadata['actortypes']
        self.df_resources = metadata['resources']
        self.df_responsetypes = metadata['responsetypes']
        self.df_metatechniques = metadata['metatechniques']
        self.it = self.create_incident_technique_crosstable(metadata['incidenttechniques'])
        self.df_tactics = metadata['tactics']

        # Add columns containing lists of techniques and counters to the tactics dataframe
        df_techniques_per_tactic = self.df_techniques.groupby('tactic_id')['id'].apply(list).reset_index().rename({'id':'technique_ids'}, axis=1)
        df_counters_per_tactic = self.df_counters.groupby('tactic_id')['id'].apply(list).reset_index().rename({'id':'counter_ids'}, axis=1)
        self.df_tactics = self.df_tactics.merge(df_techniques_per_tactic, left_on='id', right_on='tactic_id', how='left').fillna('').drop('tactic_id', axis=1)
        self.df_tactics = self.df_tactics.merge(df_counters_per_tactic, left_on='id', right_on='tactic_id', how='left').fillna('').drop('tactic_id', axis=1)

        self.phases      = self.make_object_dictionary(self.df_phases)
        self.tactics     = self.make_object_dictionary(self.df_tactics)
        self.techniques  = self.make_object_dictionary(self.df_techniques)
        self.counters    = self.make_object_dictionary(self.df_counters)
        self.metatechniques = self.make_object_dictionary(self.df_metatechniques)

        self.num_tactics = len(self.df_tactics)
        self.max_num_techniques_per_tactic = max(df_techniques_per_tactic['technique_ids'].apply(len)) +2
        self.max_num_counters_per_tactic = max(df_counters_per_tactic['counter_ids'].apply(len)) +2
        self.padded_techniques_tactics_table = self.create_padded_techniques_tactics_table()
        self.padded_counters_tactics_table = self.create_padded_counters_tactics_table()

        # Create counters cross-tables
        self.cross_counterid_techniqueid = self.splitcol(self.df_counters[['id', 'techniques']], 
                                                         'techniques', 'technique', '\n')
        self.cross_counterid_techniqueid = self.cross_counterid_techniqueid[self.cross_counterid_techniqueid['technique'].notnull()]
        self.cross_counterid_techniqueid['technique_id'] = self.cross_counterid_techniqueid['technique'].str.split(' ').str[0]
        self.cross_counterid_techniqueid.drop('technique', axis=1, inplace=True)
        
        self.cross_counterid_resource = self.splitcol(self.df_counters[['id', 'resources_needed']], 
                                                        'resources_needed', 'resource', ',')
        self.cross_counterid_resource = self.cross_counterid_resource[self.cross_counterid_resource['resource'].notnull()]


    def create_incident_technique_crosstable(self, it_metadata):
        # Generate full cross-table between incidents and techniques

        it = it_metadata
        it.index=it['id']
        it = it['technique_ids'].str.split(',').apply(lambda x: pd.Series(x)).stack().reset_index(level=1, drop=True).to_frame('technique_id').reset_index().merge(it.drop('id', axis=1).reset_index()).drop('technique_ids', axis=1)
        it = it.merge(self.df_incidents[['id','name']], 
                      left_on='incident_id', right_on='id',
                      suffixes=['','_incident']).drop('incident_id', axis=1)
        it = it.merge(self.df_techniques[['id','name']], 
                      left_on='technique_id', right_on='id',
                      suffixes=['','_technique']).drop('technique_id', axis=1)
        return(it)


    def make_object_dictionary(self, df):
        return(pd.Series(df.name.values,index=df.id).to_dict())
    
    
    def create_padded_techniques_tactics_table(self, tocsv=True):
        # Create the master grid that we make all the framework visuals from
        # cols = number of tactics
        # rows = max number of techniques per tactic + 2

        arr = [['' for i in range(self.num_tactics)] for j in range(self.max_num_techniques_per_tactic)] 
        for index, tactic in self.df_tactics.iterrows():
            arr[0][index] = tactic['phase_id']
            arr[1][index] = tactic['id']
            if tactic['technique_ids'] == '':
                continue
            for index2, technique in enumerate(tactic['technique_ids']):
                arr[index2+2][index] = technique

        #Save grid to file
        if tocsv:
            csvdir = '../generated_csvs'
            if not os.path.exists(csvdir):
                os.makedirs(csvdir)
            pd.DataFrame(arr).to_csv(csvdir + '/techniques_tactics_table.csv', index=False, header=False)

        return(arr)

    def create_padded_counters_tactics_table(self, tocsv=True):
        # Create the master grid that we make all the framework visuals from
        # cols = number of tactics
        # rows = max number of techniques per tactic + 2

        arr = [['' for i in range(self.num_tactics)] for j in range(self.max_num_counters_per_tactic)] 
        for index, tactic in self.df_tactics.iterrows():
            arr[0][index] = tactic['phase_id']
            arr[1][index] = tactic['id']
            if tactic['counter_ids'] == '':
                continue
            for index2, counter in enumerate(tactic['counter_ids']):
                arr[index2+2][index] = counter

        #Save grid to file
        if tocsv:
            csvdir = '../generated_csvs'
            if not os.path.exists(csvdir):
                os.makedirs(csvdir)
            pd.DataFrame(arr).to_csv(csvdir + '/counters_tactics_table.csv', index=False, header=False)

        return(arr)


    def splitcol(self, df, col, newcol, divider=','):
        # Thanks https://stackoverflow.com/questions/17116814/pandas-how-do-i-split-text-in-a-column-into-multiple-rows?noredirect=1
        return (df.join(df[col]
                        .str.split(divider, expand=True).stack()
                        .reset_index(drop=True,level=1)
                        .rename(newcol)).drop(col, axis=1))

    
    def create_technique_incidents_string(self, techniqueid):

        incidentstr = '''
| Incident | Descriptions given for this incident |
| -------- | -------------------- |
'''
        incirow = '| [{0} {1}](../incidents/{0}.md) | {2} |\n'
        its = self.it[self.it['id_technique']==techniqueid]
        for index, row in its[['id_incident', 'name_incident']].drop_duplicates().sort_values('id_incident').iterrows():
            techstring = ', '.join(its[its['id_incident']==row['id_incident']]['name'].to_list())
            incidentstr += incirow.format(row['id_incident'], row['name_incident'], techstring)
        return incidentstr


    def create_incident_techniques_string(self, incidentid):

        techstr = '''
| Technique | Description given for this incident |
| --------- | ------------------------- |
'''
        techrow = '| [{0} {1}](../techniques/{0}.md) | {2} {3} |\n'
        techlist = self.it[self.it['id_incident'] == incidentid]
        for index, row in techlist.sort_values('id_technique').iterrows():
            techstr += techrow.format(row['id_technique'], row['name_technique'], 
                                      row['id'], row['name'])
        return techstr


    def create_tactic_tasks_string(self, tactic_id):

        table_string = '''
| Tasks |
| ----- |
'''
        tactic_tasks = self.df_tasks[self.df_tasks['tactic_id']==tactic_id]
        task_string = '| [{0} {1}](../tasks/{0}.md) |\n'
        for index, row in tactic_tasks.sort_values('id').iterrows():
            table_string += task_string.format(row['id'], row['name'])
        return table_string


    def create_tactic_techniques_string(self, tactic_id):

        table_string = '''
| Techniques |
| ---------- |
'''
        tactic_techniques = self.df_techniques[self.df_techniques['tactic_id']==tactic_id]
        row_string = '| [{0} {1}](../techniques/{0}.md) |\n'
        for index, row in tactic_techniques.sort_values('id').iterrows():
            table_string += row_string.format(row['id'], row['name'])
        return table_string


    def create_tactic_counters_string(self, tactic_id):
        table_string = '''
| Counters | Response types |
| -------- | -------------- |
'''
        tactic_counters = self.df_counters[self.df_counters['tactic_id']==tactic_id]
        row_string = '| [{0} {1}](../counters/{0}.md) | {2} |\n'
        for index, row in tactic_counters.sort_values(['responsetype', 'id']).iterrows():
            table_string += row_string.format(row['id'], row['name'], row['responsetype'])
        return table_string


    def create_metatechnique_counters_string(self, metatechnique_id):
        table_string = '''
| Counters | Response types |
| -------- | -------------- |
'''
        metatechnique_counters = self.df_counters[self.df_counters['metatechnique_id']==metatechnique_id]
        row_string = '| [{0} {1}](../counters/{0}.md) | {2} |\n'
        for index, row in metatechnique_counters.sort_values(['responsetype', 'id']).iterrows():
            table_string += row_string.format(row['id'], row['name'], row['responsetype'])
        return table_string


    def create_technique_counters_string(self, technique_id):
        table_string = '''
| Counters |
| -------- |
'''
        technique_counters = self.cross_counterid_techniqueid[self.cross_counterid_techniqueid['technique_id']==technique_id]
        technique_counters = pd.merge(technique_counters, self.df_counters[['id', 'name']])
        row_string = '| [{0} {1}](../counters/{0}.md) |\n'
        for index, row in technique_counters.sort_values('id').iterrows():
            table_string += row_string.format(row['id'], row['name'])
        return table_string

    def create_counter_tactics_string(self, counter_id):
        table_string = '''
| Counters these Tactics |
| ---------------------- |
'''
        # tactic_counters = self.df_counters[self.df_counters['tactic_id']==tactic_id]
        # row_string = '| {0} | [{1} {2}](../counters/{1}.md) |\n'
        # for index, row in tactic_counters.sort_values(['responsetype', 'id']).iterrows():
        #     table_string += row_string.format(row['responsetype'], row['id'], row['name'])
        return table_string

    def create_counter_techniques_string(self, counter_id):
        table_string = '''
| Counters these Techniques |
| ------------------------- |
'''
        counter_techniques = self.cross_counterid_techniqueid[self.cross_counterid_techniqueid['id']==counter_id]
        counter_techniques = pd.merge(counter_techniques, self.df_techniques[['id', 'name']].rename(columns={'id': 'technique_id'}))
        row_string = '| [{0} {1}](../techniques/{0}.md) |\n'
        for index, row in counter_techniques.sort_values('id').iterrows():
            table_string += row_string.format(row['technique_id'], row['name'])
        return table_string

    def create_counter_incidents_string(self, counter_id):
        table_string = '''
| Seen in incidents |
| ----------------- |
'''
        # tactic_counters = self.df_counters[self.df_counters['tactic_id']==tactic_id]
        # row_string = '| {0} | [{1} {2}](../counters/{1}.md) |\n'
        # for index, row in tactic_counters.sort_values(['responsetype', 'id']).iterrows():
        #     table_string += row_string.format(row['responsetype'], row['id'], row['name'])
        return table_string

    def create_counter_tactic_file(self, tactic_id, datadir):
        ''' create a file summarising the counter techniques for a given tactic name

        Inside this file is:
        * A list of counters, sorted by response type
        * A list of counters that have no technique id
        * A list of counters, sorted by technique id
        For all counters that are listed for this tactic
        '''

        if not os.path.exists(datadir):
            os.makedirs(datadir)

        # Populate a list of counters for this tactic, listed by response type
        html = '''# Tactic {} {} counters\n\n'''.format(tactic_id, self.tactics[tactic_id])
        
        html += '## by action\n\n'
        for resp, counters in self.df_counters[self.df_counters['tactic_id'] == tactic_id].groupby('responsetype'):
            html += '\n### {}\n'.format(resp)
            
            for c in counters.iterrows():
                html += '* {}: {} (needs {})\n'.format(c[1]['id'], c[1]['name'],
                                                    c[1]['resources_needed'])

        # Populate a list of counters for this tactic, listed by technique
        html += '\n## by technique\n\n'
        tactecs = self.df_techniques[self.df_techniques['tactic_id'] == tactic_id]['id'].to_list()
        for tech in [tactic_id] + tactecs:
            if tech == tactic_id:
                html += '\n### {}\n'.format(tech)
            else:
                html += '\n### {} {}\n'.format(tech, self.techniques[tech])
                
            taccounts = self.cross_counterid_techniqueid[self.cross_counterid_techniqueid['technique_id'] == tech]
#            html += '\n{}\n'.format(taccounts)
            for c in self.df_counters[self.df_counters['id'].isin(taccounts['id'])].iterrows():
                html += '* {}: {} (needs {})\n'.format(c[1]['id'], c[1]['name'],
                                                    c[1]['resources_needed'])
        
        # Write the file containing the countermeasures summary for this tactic
        datafile = '../counter_tactics/{}counters.md'.format(tactic_id)
        print('Writing {}'.format(datafile))
        with open(datafile, 'w') as f:
            f.write(html)
            f.close()
        return(tactic_id)


    def create_object_file(self, index, rowtype, datadir):

        oid = index
        html = '''# {} counters: {}\n\n'''.format(rowtype, index)

        html += '## by action\n\n'
        for resp, clist in self.df_counters[self.df_counters[rowtype] == index].groupby('responsetype'):
            html += '\n### {}\n'.format(resp)

            for c in clist.iterrows():
                html += '* {}: {} (needs {})\n'.format(c[1]['id'], c[1]['name'],
                                                    c[1]['resources_needed'])

        datafile = '{}/{}counters.md'.format(datadir, oid)
        print('Writing {}'.format(datafile))
        with open(datafile, 'w') as f:
            f.write(html)
            f.close()
        return(oid)


    def write_object_index_to_file(self, objectname, objectcols, dfobject, outfile):
        ''' Write HTML version of incident list to markdown file

        Assumes that dfobject has columns named 'id' and 'name'
        '''

        html = '''# AMITT {}:

<table border="1">
<tr>
'''.format(objectname.capitalize())

        # Create header row
        html += '<th>{}</th>\n'.format('id')
        html += ''.join(['<th>{}</th>\n'.format(col) for col in objectcols])
        html += '</tr>\n'

        # Add row for each object
        for index, row in dfobject[dfobject['name'].notnull()].iterrows():
            html += '<tr>\n'
            html += '<td><a href="{0}/{1}.md">{1}</a></td>\n'.format(objectname, row['id'])
            html += ''.join(['<td>{}</td>\n'.format(row[col]) for col in objectcols])
            html += '</tr>\n'
        html += '</table>\n'

        # Write file
        with open(outfile, 'w') as f:
            f.write(html)
            print('updated {}'.format(outfile))
        return

    def write_object_indexes_to_file(self):
        ''' Create an index file for each object type.
        '''
        self.write_object_index_to_file(
            'response types', ['name', 'summary'],
            self.df_responsetypes, '../responsetype_index.md')
        self.write_object_index_to_file(
            'metatechniques', ['name', 'summary'],
            self.df_metatechniques, '../metatechniques_index.md')
        self.write_object_index_to_file(
            'actortypes', ['name', 'summary'],
            self.df_actortypes, '../actortypes_index.md')
        self.write_object_index_to_file(
            'detections', ['name', 'summary', 'metatechnique', 'tactic', 'responsetype'],
            self.df_detections, '../detections_index.md')

        return

    def update_markdown_files(self):
        ''' Create or update all the editable markdown files in the repo

        Reads in any user-written text before updating the header information above it
        Does this for phase, tactic, technique, task, incident and counter objects
        '''

        warntext = 'DO NOT EDIT ABOVE THIS LINE - PLEASE ADD NOTES BELOW'
        warnlen = len(warntext)
        
        metadata = {
            'phase': self.df_phases,
            'tactic': self.df_tactics,
            'technique': self.df_techniques,
            'task': self.df_tasks,
            'incident': self.df_incidents,
            'counter': self.df_counters,
            'metatechnique': self.df_metatechniques,
            'actortype': self.df_actortypes,
            #'responsetype': self.df_responsetypes,
            #'detection': self.df_detections
        }
        
        indexrows = {
            'phase': ['name', 'summary'],
            'tactic': ['name', 'summary', 'phase_id'],
            'technique': ['name', 'summary', 'tactic_id'],
            'task': ['name', 'summary', 'tactic_id'],
            'incident': ['name', 'type', 'Year Started', 'To country', 'Found via'],
            'counter': ['name', 'summary', 'metatechnique', 'tactic', 'responsetype'],
            'detection': ['name', 'summary', 'metatechnique', 'tactic', 'responsetype'],
            'responsetype': ['name', 'summary'],
            'metatechnique': ['name', 'summary'],
            'actortype': ['name', 'summary']
        }
        
        for objecttype, df in metadata.items():

            # Create objecttype directory if needed.  Create index file for objecttype
            objecttypeplural = objecttype + 's'
            objecttypedir = '../{}'.format(objecttypeplural)
            if not os.path.exists(objecttypedir):
                os.makedirs(objecttypedir)
            self.write_object_index_to_file(objecttypeplural, indexrows[objecttype],
                                            metadata[objecttype], 
                                            '../{}_index.md'.format(objecttypeplural))

            # Update or create file for every object with this objecttype type
            template = open('template_{}.md'.format(objecttype)).read()
            for index, row in df[df['name'].notnull()].iterrows():

                # First read in the file - if it exists - and grab everything 
                # below the "do not write about this line". Will write this 
                # out below new metadata. 
                datafile = '../{}/{}.md'.format(objecttypeplural, row['id'])
                oldmetatext = ''
                if os.path.exists(datafile):
                    with open(datafile) as f:
                        filetext = f.read()
                    warnpos = filetext.find(warntext)
                    if warnpos == -1:
                        print('no warning text found in {}: adding to file'.format(datafile))
                        usertext = filetext
                    else:
                        oldmetatext = filetext[:warnpos+warnlen]
                        usertext = filetext[warnpos+warnlen:]
                else:
                    usertext = ''

                # Now populate datafiles with new metadata plus old userdata
                if objecttype == 'phase':
                    metatext = template.format(type='Phase', id=row['id'], name=row['name'], summary=row['summary'])
                if objecttype == 'tactic':
                    metatext = template.format(type = 'Tactic', id=row['id'], name=row['name'],
                                               phase=row['phase_id'], summary=row['summary'],
                                               tasks=self.create_tactic_tasks_string(row['id']),
                                               techniques=self.create_tactic_techniques_string(row['id']),
                                               counters=self.create_tactic_counters_string(row['id']))
                if objecttype == 'task':
                    metatext = template.format(type='Task', id=row['id'], name=row['name'],
                                               tactic=row['tactic_id'], summary=row['summary'])
                if objecttype == 'technique':
                    metatext = template.format(type = 'Technique', id=row['id'], name=row['name'],
                                               tactic=row['tactic_id'], summary=row['summary'],
                                               incidents=self.create_technique_incidents_string(row['id']),
                                               counters=self.create_technique_counters_string(row['id']))
                if objecttype == 'counter':
                    metatext = template.format(type = 'Counter', id=row['id'], name=row['name'],
                                               tactic=row['tactic_id'], summary=row['summary'],
                                               playbooks=row['playbooks'], metatechnique=row['metatechnique'],
                                               resources_needed=row['resources_needed'],
                                               tactics=self.create_counter_tactics_string(row['id']),
                                               techniques=self.create_counter_techniques_string(row['id']),
                                               incidents=self.create_counter_incidents_string(row['id']))
                if objecttype == 'incident':
                    metatext = template.format(type = 'Incident', id=row['id'], name=row['name'],
                                               incidenttype=row['type'], summary=row['summary'],
                                               yearstarted=row['Year Started'], 
                                               fromcountry=row['From country'],
                                               tocountry=row['To country'],
                                               foundvia=row['Found via'],
                                               dateadded=row['When added'],
                                               techniques=self.create_incident_techniques_string(row['id']))
                if objecttype == 'actortype':
                    metatext = template.format(type = 'Actor Type', id=row['id'], name=row['name'], 
                                               summary=row['summary'])
                if objecttype == 'metatechnique':
                    metatext = template.format(type='Metatechnique', id=row['id'], name=row['name'], 
                                               summary=row['summary'],
                                               counters=self.create_metatechnique_counters_string(row['id']))

                # Make sure the user data goes in
                if (metatext + warntext) != oldmetatext:
                    print('Updating {}'.format(datafile))
                    with open(datafile, 'w') as f:
                        f.write(metatext)
                        f.write(warntext)
                        f.write(usertext)
                        f.close()
        return


    def write_amitt_red_framework_file(self, outfile = '../amitt_red_framework.md'):
        # Write HTML version of framework diagram to markdown file
        # Needs phases, tactics, techniques, padded_techniques_tactics_table

        html = '''# AMITT Red: Latest Framework

<table border="1">
<tr>
'''

        # for col in range(self.num_tactics):
        #     html += '<td><a href="phases/{0}.md">{0} {1}</a></td>\n'.format(
        #         self.padded_techniques_tactics_table[0][col], self.phases[self.padded_techniques_tactics_table[0][col]])
        # html += '</tr>\n'

        html += '<tr style="background-color:blue;color:white;">\n'
        for col in range(self.num_tactics):
            html += '<td><a href="tactics/{0}.md">{0} {1}</a></td>\n'.format(
                self.padded_techniques_tactics_table[1][col], self.tactics[self.padded_techniques_tactics_table[1][col]])
        html += '</tr>\n<tr>\n'

        for row in range(2,self.max_num_techniques_per_tactic):
            for col in range(self.num_tactics):
                if self.padded_techniques_tactics_table[row][col] == '':
                    html += '<td> </td>\n'
                else:
                    html += '<td><a href="techniques/{0}.md">{0} {1}</a></td>\n'.format(
                        self.padded_techniques_tactics_table[row][col], self.techniques[self.padded_techniques_tactics_table[row][col]])
            html += '</tr>\n<tr>\n'
        html += '</tr>\n</table>\n'

        with open(outfile, 'w') as f:
            f.write(html)
            print('updated {}'.format(outfile))
        return

    def write_amitt_blue_framework_file(self, outfile = '../amitt_blue_framework.md'):
        # Write HTML version of counters framework diagram to markdown file
        # Needs phases, tactics, counters, padded_counters_tactics_table

        html = '''# AMITT Blue: Latest Framework

<table border="1">
<tr>
'''

        # for col in range(self.num_tactics):
        #     html += '<td><a href="phases/{0}.md">{0} {1}</a></td>\n'.format(
        #         self.padded_counters_tactics_table[0][col], self.phases[self.padded_counters_tactics_table[0][col]])
        # html += '</tr>\n'

        html += '<tr style="background-color:blue;color:white;">\n'
        for col in range(self.num_tactics):
            html += '<td><a href="tactics/{0}.md">{0} {1}</a></td>\n'.format(
                self.padded_counters_tactics_table[1][col], self.tactics[self.padded_counters_tactics_table[1][col]])
        html += '</tr>\n<tr>\n'

        for row in range(2,self.max_num_counters_per_tactic):
            for col in range(self.num_tactics):
                if self.padded_counters_tactics_table[row][col] == '':
                    html += '<td> </td>\n'
                else:
                    html += '<td><a href="counters/{0}.md">{0} {1}</a></td>\n'.format(
                        self.padded_counters_tactics_table[row][col], self.counters[self.padded_counters_tactics_table[row][col]])
            html += '</tr>\n<tr>\n'
        html += '</tr>\n</table>\n'

        with open(outfile, 'w') as f:
            f.write(html)
            print('updated {}'.format(outfile))
        return



    def write_clickable_amitt_red_framework_file(self, outfile='../amitt_red_framework_clickable.html'):
        # Write clickable html version of the matrix grid to html file

        html = '''<!DOCTYPE html>
<html>
<head>
    <title>AMITT</title>
</head>
<body>

<script>
function handleTechniqueClick(box) {
  var technique = document.getElementById(box);
  var checkBox = document.getElementById(box+"check");
  var text = document.getElementById(box+"text");
  if (checkBox.checked == true){
    text.style.display = "block";
    technique.bgColor = "Lime"
  } else {
     text.style.display = "none";
     technique.bgColor = "Silver"
  }
}
</script>

<h1>AMITT</h1>

<table border=1 bgcolor=silver>
'''

        html += '<tr bgcolor=fuchsia>\n'
        for col in range(self.num_tactics):
            html += '<td>{0} {1}</td>\n'.format(self.padded_techniques_tactics_table[0][col], self.phases[self.padded_techniques_tactics_table[0][col]])
        html += '</tr>\n'

        html += '<tr bgcolor=aqua>\n'
        for col in range(self.num_tactics):
            html += '<td>{0} {1}</td>\n'.format(self.padded_techniques_tactics_table[1][col], self.tactics[self.padded_techniques_tactics_table[1][col]])
        html += '</tr>\n'

        liststr = ''
        html += '<tr>\n'
        for row in range(2,self.max_num_techniques_per_tactic):
            for col in range(self.num_tactics):
                techid = self.padded_techniques_tactics_table[row][col]
                if techid == '':
                    html += '<td bgcolor=white> </td>\n'
                else:
                    html += '<td id="{0}">{0} {1}<input type="checkbox" id="{0}check"  onclick="handleTechniqueClick(\'{0}\')"></td>\n'.format(
                        techid, self.techniques[techid])
                    liststr += '<li id="{0}text" style="display:none">{0}: {1}</li>\n'.format(
                        techid, self.techniques[techid])

            html += '</tr>\n<tr>\n'
        html += '</tr>\n</table>\n<hr>\n'

        html += '<ul>\n{}</ul>\n'.format(liststr)
        html += '''
</body>
</html>
'''

        with open(outfile, 'w') as f:
            f.write(html)
            print('updated {}'.format(outfile))
        return

        
    def print_technique_incidents(self):
        for id_technique in self.df_techniques['id'].to_list():
            print('{}\n{}'.format(id_technique, 
                                  self.create_incidentstring(id_technique)))
        return


    def print_incident_techniques(self):
        for id_incident in self.df_incidents['id'].to_list():
            print('{}\n{}'.format(id_incident, 
                                  self.create_techstring(id_incident)))
        return

    
    def generate_and_write_datafiles(self):

        self.update_markdown_files()
        self.write_object_indexes_to_file()
        self.write_amitt_red_framework_file()
        self.write_amitt_blue_framework_file()
        self.write_clickable_amitt_red_framework_file()
        self.write_responsetype_tactics_table_file()
        self.write_metatechniques_responsetype_table_file()
        self.write_resources_responsetype_table_file()
        
        return

        
    def analyse_counter_text(self, col='name'):
        # Analyse text in counter descriptions
        alltext = (' ').join(self.df_counters[col].to_list()).lower()
        count_vect = CountVectorizer(stop_words='english')
        word_counts = count_vect.fit_transform([alltext])
        dfw = pd.DataFrame(word_counts.A, columns=count_vect.get_feature_names()).transpose()
        dfw.columns = ['count']
        dfw = dfw.sort_values(by='count', ascending=False)
        return(dfw)   

    
    # Print list of counters for each square of the COA matrix
    # Write HTML version of framework diagram to markdown file
    def write_responsetype_tactics_table_file(self, outfile = '../tactics_by_responsetype_table.md'):
        ''' fill the counter_tactics directory

        One file for every tactic, plus a file for "ALL" tactics
        Inside each file:
        * A list of counters, sorted by response type
        * A list of counters that have no technique id
        * A list of counters, sorted by technique id
        For all counters that are listed for this tactic
        '''

        datadirname = 'counter_tactics'
        datadir = '../' + datadirname

        coacounts = pd.pivot_table(self.df_counters[['tactic_id', 'responsetype',
                                                    'id']], index='responsetype', columns='tactic_id', aggfunc=len, fill_value=0)

        html = '''# AMITT Courses of Action matrix:

<table border="1">
<tr>
<td> </td>
'''
        #Table heading = tactic names
        for col in coacounts.columns.get_level_values(1):
            tid = self.create_counter_tactic_file(col, datadir)
            html += '<td><a href="{0}/{1}counters.md">{2}</a></td>\n'.format(
                datadir, tid, col)
        html += '</tr><tr>\n'

        # number of counters per response type
        for responsetype, counts in coacounts.iterrows(): 
            html += '<td>{}</td>\n'.format(responsetype)
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


    def write_metatechniques_responsetype_table_file(self, outfile = '../metatechniques_by_responsetype_table.md'):

        coltype = 'responsetype'
        rowtype = 'metatechnique_id'
        rowname = 'metatag'
        datadirname = 'metatechniques'
        datadir = '../' + datadirname
        mtcounts = pd.pivot_table(self.df_counters[[coltype, rowtype,'id']], 
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
        if not os.path.exists(datadir):
            os.makedirs(datadir)
        for index, counts in mtcounts.iterrows(): 
            html += '<td><a href="{0}/{1}.md">{1} {2}</a></td>\n'.format(
                datadirname, index, self.metatechniques[index])
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


    def create_resource_file(self, index, rowtype, datadir):
        oid = index
        counterrows = self.cross_counterid_resource[self.cross_counterid_resource['resource'] == index]['id'].to_list()
        html = '''# {} counters: {}\n\n'''.format(rowtype, index)
        html += '## by action\n\n'
        omatrix = self.df_counters[self.df_counters['id'].isin(counterrows)].groupby('responsetype')
        for resp, clist in omatrix:
            html += '\n### {}\n'.format(resp)
            for c in clist.iterrows():
                html += '* {}: {} (needs {})\n'.format(c[1]['id'], c[1]['name'],
                                                    c[1]['resources_needed'])

        datafile = '{}/{}counters.md'.format(datadir, oid)
        print('Writing {}'.format(datafile))
        with open(datafile, 'w') as f:
            f.write(html)
            f.close()
        return(oid, omatrix)


    def write_resources_responsetype_table_file(self, outfile = '../resources_by_responsetype_table.md'):

        coltype = 'responsetype'
        rowtype = 'resource'
        rowname = 'resource'
        datadirname = 'resources_needed'
        datadir = '../' + datadirname

        html = '''# AMITT {} courses of action

<table border="1">
<tr>
<td> </td>
'''.format(rowtype)

        # Table heading row
        colvals = self.df_counters[coltype].value_counts().sort_index().index
        for col in colvals:
            html += '<td>{}</td>\n'.format(col)
        html += '<td>TOTALS</td></tr><tr>\n'

        # Data rows
        if not os.path.exists(datadir):
            os.makedirs(datadir)
        for index in self.cross_counterid_resource['resource'].value_counts().sort_index().index:
            (oid, omatrix) = self.create_resource_file(index, rowtype, datadir) #self
            row = pd.DataFrame(omatrix.apply(len), index=colvals).fillna(' ')
            html += '<td><a href="{0}/{1}counters.md">{2}</a></td>\n'.format(
                datadirname, oid, index)
            if len(row.columns) > 0:
                for val in row[0].to_list():
                    html += '<td>{}</td>\n'.format(val)
            html += '<td>{}</td></tr>\n<tr>\n'.format('')

        html += '</tr>\n</table>\n'           

        with open(outfile, 'w') as f:
            f.write(html)
            print('updated {}'.format(outfile))

        return



def main():
    amitt = Amitt()
    amitt.generate_and_write_datafiles()


if __name__ == "__main__":
    main()
