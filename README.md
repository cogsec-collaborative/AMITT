# AMITT Disinformation Tactics, Techniques and Processes (TTP) Framework

* [Framework diagram](matrix.md)
* [List of incidents](incidents.md)
* [Counters matrix](counter_tactic_counts.md)

AMITT (Adversarial Misinformation and Influence Tactics and Techniques) is a framework designed for describing and understanding disinformation incidents.  AMITT is part of work on adapting information security (infosec) practices to help track and counter misinformation, and is designed to fit existing infosec practices and tools. 

AMITT's style is based on the [MITRE ATT&amp;CK framework](https://github.com/mitre-attack/attack-website/); STIX templates for AMITT objects are available in the [AMITT_CTI repo](https://github.com/cogsec-collaborative/amitt_cti) - these make it easy for AMITT data to be passed between ISAOs and similar bodies using standards like TAXI. 

AMITT design documents are available in the AMITT_HISTORY folder, and in [The AMITT Design Guide](https://docs.google.com/document/d/1D1VM5l496pUjN8B5Pq6fAh9mgeeEaYTKHdAG5BEXBiA/edit#).   

## RAW DATA

If you want to do your own thing with AMITT data, all the master data for it is in directory [AMITT_MASTER_DATA](AMITT_MASTER_DATA). Look for 
* [the TTP framework](AMITT_MASTER_DATA/amitt_metadata_v3.xlsx) spreadsheet. This contains disinformation creators' tactics, techniques, tasks and phases. 
* [countermeasures](AMITT_MASTER_DATA/CountersPlaybook_MASTER.xlsx) spreadsheet. This contains defences and mitigations for disinformation, categorised by disinformation technique, resources needed, etc.  

## Red Team Tactics (TTP Framework) HTML pages

The disinformation "red team" framework is shown in [Framework diagram](matrix.md). Its entities are:
* Tactics: stages that someone running a misinformation incident is likely to use
* Techniques: activities that might be seen at each stage
* Tasks: things that need to be done at each stage.  In Pablospeak, tasks are things you do, techniques are how you do them. 
* Phases: higher-level groupings of tactics, created so we could check we didn't miss anything

There's a directory for each of these entities, containing a datasheet for each individual entity (e.g. [technique T0046 Search Engine Optimization](techniques/T0046.md)).  The details above "DO NOT EDIT ABOVE THIS LINE" are generated from the code and spreadsheet in folder generating_code, which you can use to update framework metadata; you can add notes below "DO NOT EDIT ABOVE THIS LINE" and they won't be removed when you do metadata updates.  (Yes, this is an unholy hack, but it's one that lets us generate all the messages we need, and keep notes in the same place.)

The framework was created by finding and analysing a set of existing misinformation [incidents](incidents.md), which also have room for more notes.

## Blue Team Tactics (Countermeasures) HTML pages

Countermeasures are shown grouped by:

* Red team tactic stage and technique (see https://github.com/misinfosecproject/amitt_framework for descriptions of these) in directory [tactics](tactics), with a clickable grid for this in [counter_tactic_counts.md](counter_tactic_counts.md) 
* A higher-level label, "metatechnique",in directory [counter_metatag](counter_metatag), with a clickable grid for this in [counter_metatag_counts.md](counter_metatag_counts.md) (To be fair this is mostly so we can group and make sure we're getting the cleaning right.) 
* The types of people who can respond [counter_resource_counts.md](counter_resource_counts.md).

## Updating the HTML pages

The code to create all the HTML datasheets is in directory [HTML_GENERATING_CODE](HTML_GENERATING_CODE)

* If you change something in the metadata file, go into generating_code, and type "python amitt.py" - this will update the metadata in all the datasheets, and create a datasheet each for any new objects you've added to the spreadsheet.
* If you change anything in the countermeasures spreadsheet, typing "python counter.py" creates all html pages for countermeasures.

## Provenance

The AMITT Framework and Countermeasures were created by the Credibility Coalition's [Misinfosec working group](https://github.com/credcoalition/community-site/wiki/Working-Groups). The Framework was started in December 2018 and refined in a Credibility Coalition Misinfosec seminar; the collection of potential disinformation countermeasures was started at a Credibility Coalition Misinfosec seminar in November 2019.  

AMITT is currently maintained by the [CogSecCollab](http://cogsec-collab.org/), who've used it in the CTI League's Covid19 responses, and tested it in trials with NATO, the EU, and several other countries' disinformation units.

We would like to thank everyone who's contributed to, and continues to contribute to AMITT over the years.  We'd also love any and all suggestions for improvements, comments and offers of help - either reach out to us, or add to this repo's issues list. 


AMITT is licensed under [CC-BY-4.0](LICENSE.md)
