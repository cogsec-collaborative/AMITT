# AMITT Disinformation Tactics, Techniques and Processes (TTP) Framework

AMITT (Adversarial Misinformation and Influence Tactics and Techniques) is a framework designed for describing and understanding disinformation incidents.  AMITT is part of work on adapting information security (infosec) practices to help track and counter misinformation, and is designed to fit existing infosec practices and tools. 

AMITT's style is based on the [MITRE ATT&amp;CK framework](https://github.com/mitre-attack/attack-website/); STIX templates for AMITT objects are available in the [AMITT_CTI repo](https://github.com/cogsec-collaborative/amitt_cti) - these make it easy for AMITT data to be passed between ISAOs and similar bodies using standards like TAXI. 

AMITT design documents are available in the AMITT_HISTORY folder, and in [The AMITT Design Guide](https://docs.google.com/document/d/1D1VM5l496pUjN8B5Pq6fAh9mgeeEaYTKHdAG5BEXBiA/edit#).   

## What's in this folder

The AMITT framework diagrams are: 
* [AMITT Red Team Framework](amitt_red_framework.md) - Disinformation creator TTPs, listed by tactic stage. This is the classic "AMITT Framework" that's bundled with MISP.  The [clickable](amitt_red_framework_clickable.html) version is for rapidly creating lists of TTPs. 

All the entities used to create the Red Team and Blue Team frameworks: 
* [Phases](phases): higher-level groupings of tactics, created so we could check we didn't miss anything
* [Tactics](tactics): stages that someone running a misinformation incident is likely to use
* [Techniques](techniques): activities that might be seen at each stage
* [Tasks](tasks): things that need to be done at each stage.  In Pablospeak, tasks are things you do, techniques are how you do them. 
* [Counters](counters): countermeasures to AMITT TTPs.  
* [Resources_needed](resources_needed): resources needed to run countermeasures - index is [resources_by_responsetype_table](resources_by_responsetype_table.md)
* [Metatechniques](metatechniques): a higher-level grouping for countermeasures - index is [metatechniques_by_responsetype_table](metatechniques_by_responsetype_table.md)
* [Incidents](incidents): incident descriptions used to create the AMITT frameworks - index is [incidents_list](incidents_list.md)

There's a directory for each of these, containing a datasheet for each individual entity (e.g. [technique T0046 Search Engine Optimization](techniques/T0046.md)).  

YOU CAN ADD INFORMATION TO THESE FILES.
* The details above "DO NOT EDIT ABOVE THIS LINE" are generated and will be overwritten every time we run the update code; anything you write above that line will be lost
* The details below "DO NOT EDIT ABOVE THIS LINE" are saved every time we run the update code. You can safely add notes below that line. 

[generated_csvs](generated_csvs) contains any CSV files we generate from the above tables. 


## Using the Raw Data file

If you want to do your own thing with AMITT data, all the master data for it is in directory [AMITT_MASTER_DATA](AMITT_MASTER_DATA). Look for the [AMITT_TTPs_MASTER.xlsx](AMITT_MASTER_DATA/AMITT_TTPs_MASTER.xlsx) spreadsheet. This contains disinformation creators' tactics, techniques, tasks, phases, and counters. 

The [AMITT TTP Guide](https://docs.google.com/document/d/1Kc0O7owFyGiYs8N8wSq17gRUPEDQsD5lLUL_3KGCgRE/edit#) has more detailed information on each technique. 

The code to create all the HTML datasheets is in directory [HTML_GENERATING_CODE](HTML_GENERATING_CODE). If you have your own version of this repository and update AMITT_TTPs_MASTER.xlsx, typing "python generate_amitt_ttps.py" will update all the files above from it. 


## Who's Responsible for AMITT

AMITT is currently maintained by the [CogSecCollab](http://cogsec-collab.org/), who've used it in the CTI League's Covid19 responses, and tested it in trials with NATO, the EU, and several other countries' disinformation units.

The AMITT Framework and Countermeasures were created by the Credibility Coalition's [Misinfosec working group](https://github.com/credcoalition/community-site/wiki/Working-Groups). The Framework was started in December 2018 and refined in a Credibility Coalition Misinfosec seminar; the collection of potential disinformation countermeasures was started at a Credibility Coalition Misinfosec seminar in November 2019.  

We would like to thank everyone who's contributed to, and continues to contribute to AMITT over the years.  We'd also love any and all suggestions for improvements, comments and offers of help - either reach out to us, or add to this repo's [issues list](https://github.com/cogsec-collaborative/AMITT/issues). (We're also going back through the [original issues list](https://github.com/misinfosecproject/amitt_framework/issues) too)


AMITT is licensed under [CC-BY-4.0](LICENSE.md)
