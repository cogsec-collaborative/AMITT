''' Manage AMITT metadata

Create a page for each of the AMITT objects, if it doesn't already exist.
If it does exist, update the metadata on it, and preserve any hand-
created notes below the metadata area in it.

* todo: add all framework comments to the repo issues list
'''

import pandas as pd
import numpy as np
import os


class Amitt:

    
    def __init__(self, infile = '../AMITT_MASTER_DATA/AMITT_TTPs_MASTER.xlsx'):
        
        # Load metadata from file
        metadata = {}
        xlsx = pd.ExcelFile(infile)
        for sheetname in xlsx.sheet_names:
            metadata[sheetname] = xlsx.parse(sheetname)

        # Create individual tables and dictionaries
        self.phases = metadata['phases']
        self.techniques = metadata['techniques']
        self.tasks = metadata['tasks']
        self.incidents = metadata['incidents']
        self.it = self.create_incident_technique_crosstable(metadata['incidenttechniques'])

        tactechs = self.techniques.groupby('tactic')['id'].apply(list).reset_index().rename({'id':'techniques'}, axis=1)
        self.tactics = metadata['tactics'].merge(tactechs, left_on='id', right_on='tactic', how='left').fillna('').drop('tactic', axis=1)

        self.phasedict = self.make_object_dict(self.phases)
        self.tacdict   = self.make_object_dict(self.tactics)
        self.techdict  = self.make_object_dict(self.techniques)

        self.ngridrows = max(tactechs['techniques'].apply(len)) +2
        self.ngridcols = len(self.tactics)
        self.grid = self.create_display_grid()


    def create_incident_technique_crosstable(self, it_metadata):
        # Generate full cross-table between incidents and techniques

        it = it_metadata
        it.index=it['id']
        it = it['techniques'].str.split(',').apply(lambda x: pd.Series(x)).stack().reset_index(level=1, drop=True).to_frame('technique').reset_index().merge(it.drop('id', axis=1).reset_index()).drop('techniques', axis=1)
        it = it.merge(self.incidents[['id','name']], 
                      left_on='incident', right_on='id',
                      suffixes=['','_incident']).drop('incident', axis=1)
        it = it.merge(self.techniques[['id','name']], 
                      left_on='technique', right_on='id',
                      suffixes=['','_technique']).drop('technique', axis=1)
        return(it)


    def make_object_dict(self, df):
        return(pd.Series(df.name.values,index=df.id).to_dict())
    
    
    def create_display_grid(self, tofile=True):
        # Create the master grid that we make all the framework visuals from
        # cols = number of tactics
        # rows = max number of techniques per tactic + 2

        arr = [['' for i in range(self.ngridcols)] for j in range(self.ngridrows)] 
        for index, tactic in self.tactics.iterrows():
            arr[0][index] = tactic['phase']
            arr[1][index] = tactic['id']
            if tactic['techniques'] == '':
                continue
            for index2, technique in enumerate(tactic['techniques']):
                arr[index2+2][index] = technique

        #Save grid to file
        if tofile:
            matrixdir = '../matrices'
            if not os.path.exists(matrixdir):
                os.makedirs(matrixdir)
            pd.DataFrame(arr).to_csv(matrixdir + '/matrix_arr.csv', index=False, header=False)

        return(arr)


    def create_incidentstring(self, techniqueid):

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


    def create_techstring(self, incidentid):

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


    def create_taskstring(self, tacticid):

        taskstr = '''
| Task |
| ---- |
'''
        tasklist = self.tasks[self.tasks['tactic']==tacticid]
        taskrow = '| [{0} {1}](../tasks/{0}.md) |\n'
        for index, row in tasklist.sort_values('id').iterrows():
            taskstr += taskrow.format(row['id'], row['name'])
        return taskstr


    def create_techtacstring(self, tacticid):

        techstr = '''
| Technique |
| --------- |
'''
        techlist = self.techniques[self.techniques['tactic']==tacticid]
        techrow = '| [{0} {1}](../techniques/{0}.md) |\n'
        for index, row in techlist.sort_values('id').iterrows():
            techstr += techrow.format(row['id'], row['name'])
        return techstr


    def generate_datasheets(self):
        # Generate datafiles
        warntext = 'DO NOT EDIT ABOVE THIS LINE - PLEASE ADD NOTES BELOW'
        warnlen = len(warntext)
        
        metadata = {
            'phase': self.phases,
            'tactic': self.tactics,
            'technique': self.techniques,
            'task': self.tasks,
            'incident': self.incidents
        }
        
        for entity, df in metadata.items():
            entities = entity + 's'
            entitydir = '../{}'.format(entities)
            if not os.path.exists(entitydir):
                os.makedirs(entitydir)

            template = open('template_{}.md'.format(entity)).read()
            for index, row in df[df['name'].notnull()].iterrows():

                # First read in the file - if it exists - and grab everything 
                # below the "do not write about this line". Will write this 
                # out below new metadata. 
                datafile = '../{}/{}.md'.format(entities, row['id'])
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
                if entity == 'phase':
                    metatext = template.format(id=row['id'], name=row['name'], summary=row['summary'])
                if entity == 'tactic':
                    metatext = template.format(id=row['id'], name=row['name'],
                                               phase=row['phase'], summary=row['summary'],
                                               tasks=self.create_taskstring(row['id']),
                                               techniques=self.create_techtacstring(row['id']))
                if entity == 'task':
                    metatext = template.format(id=row['id'], name=row['name'],
                                               tactic=row['tactic'], summary=row['summary'])
                if entity == 'technique':
                    metatext = template.format(id=row['id'], name=row['name'],
                                               tactic=row['tactic'], summary=row['summary'],
                                               incidents=self.create_incidentstring(row['id']))
                if entity == 'incident':
                    metatext = template.format(id=row['id'], name=row['name'],
                                               type=row['type'], summary=row['summary'],
                                               yearstarted=row['Year Started'], 
                                               fromcountry=row['From country'],
                                               tocountry=row['To country'],
                                               foundvia=row['Found via'],
                                               dateadded=row['When added'],
                                               techniques=self.create_techstring(row['id']))

                # Make sure the user data goes in
                if (metatext + warntext) != oldmetatext:
                    print('Updating {}'.format(datafile))
                    with open(datafile, 'w') as f:
                        f.write(metatext)
                        f.write(warntext)
                        f.write(usertext)
                        f.close()
        return


    def write_grid_markdown(self, outfile = '../matrix.md'):
        # Write HTML version of framework diagram to markdown file
        # Needs phasedict, tacdict, techdict, grid

        html = '''# AMITT Latest Framework:

<table border="1">
<tr>
'''

        for col in range(self.ngridcols):
            html += '<td><a href="phases/{0}.md">{0} {1}</a></td>\n'.format(
                self.grid[0][col], self.phasedict[self.grid[0][col]])
        html += '</tr>\n'

        html += '<tr style="background-color:blue;color:white;">\n'
        for col in range(self.ngridcols):
            html += '<td><a href="tactics/{0}.md">{0} {1}</a></td>\n'.format(
                self.grid[1][col], self.tacdict[self.grid[1][col]])
        html += '</tr>\n<tr>\n'

        for row in range(2,self.ngridrows):
            for col in range(self.ngridcols):
                if self.grid[row][col] == '':
                    html += '<td> </td>\n'
                else:
                    html += '<td><a href="techniques/{0}.md">{0} {1}</a></td>\n'.format(
                        self.grid[row][col], self.techdict[self.grid[row][col]])
            html += '</tr>\n<tr>\n'
        html += '</tr>\n</table>\n'

        with open(outfile, 'w') as f:
            f.write(html)
            print('updated {}'.format(outfile))
        return


    def write_incidentlist_markdown(self, outfile='../incidents.md'):
        # Write HTML version of incident list to markdown file

        html = '''# AMITT Incidents:

<table border="1">
<tr>
'''

        cols = ['name', 'type', 'Year Started', 'From country', 'To country',
                'Found via']

        html += '<th>{}</th>\n'.format('id')
        for col in cols:
            html += '<th>{}</th>\n'.format(col)
        html += '</tr>\n'

        for index, row in self.incidents[self.incidents['name'].notnull()].iterrows():
            html += '<tr>\n'
            html += '<td><a href="incidents/{0}.md">{0}</a></td>\n'.format(row['id'])
            for col in cols:
                    html += '<td>{}</td>\n'.format(row[col])
            html += '</tr>\n'
        html += '</table>\n'
        with open(outfile, 'w') as f:
            f.write(html)
            print('updated {}'.format(outfile))
        return


    def write_grid_message_generator(self, outfile='../matrix_to_message.html'):
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
        for col in range(self.ngridcols):
            html += '<td>{0} {1}</td>\n'.format(self.grid[0][col], self.phasedict[self.grid[0][col]])
        html += '</tr>\n'

        html += '<tr bgcolor=aqua>\n'
        for col in range(self.ngridcols):
            html += '<td>{0} {1}</td>\n'.format(self.grid[1][col], self.tacdict[self.grid[1][col]])
        html += '</tr>\n'

        liststr = ''
        html += '<tr>\n'
        for row in range(2,self.ngridrows):
            for col in range(self.ngridcols):
                techid = self.grid[row][col]
                if techid == '':
                    html += '<td bgcolor=white> </td>\n'
                else:
                    html += '<td id="{0}">{0} {1}<input type="checkbox" id="{0}check"  onclick="handleTechniqueClick(\'{0}\')"></td>\n'.format(
                        techid, self.techdict[techid])
                    liststr += '<li id="{0}text" style="display:none">{0}: {1}</li>\n'.format(
                        techid, self.techdict[techid])

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
        for id_technique in self.techniques['id'].to_list():
            print('{}\n{}'.format(id_technique, 
                                  self.create_incidentstring(id_technique)))
        return


    def print_incident_techniques(self):
        for id_incident in self.incidents['id'].to_list():
            print('{}\n{}'.format(id_incident, 
                                  self.create_techstring(id_incident)))
        return

    
    def generate_datafiles(self):
        
        self.generate_datasheets()
        self.write_grid_markdown()
        self.write_incidentlist_markdown()
        self.write_grid_message_generator()
        
        return

 
def main():
    amitt = Amitt()
    amitt.generate_datafiles()


if __name__ == "__main__":
    main()
