# AMITT Disinformation Tactics, Techniques and Processes (TTP) Framework

AMITT (Adversarial Misinformation and Influence Tactics and Techniques) is a framework designed for describing and understanding disinformation incidents.  AMITT is part of work on adapting information security (infosec) practices to help track and counter misinformation, and is designed to fit existing infosec practices and tools. 

AMITT's style is based on the [MITRE ATT&amp;CK framework](https://github.com/mitre-attack/attack-website/); STIX templates for AMITT objects are available in the [AMITT_CTI repo](https://github.com/cogsec-collaborative/amitt_cti) - these make it easy for AMITT data to be passed between ISAOs and similar bodies using standards like TAXI. 

## What's in this folder

AMITT DOCUMENTATION:
* [AMITT_GUIDES](AMITT_GUIDES): AMITT user guides, design guides, and more detailed TTP documentation.
* [AMITT_HISTORY](AMITT_HISTORY): earlier models and reports.

AMITT FRAMEWORKS: 
* [AMITT Red Team Framework](amitt_red_framework.md) - Disinformation creator TTPs, listed by tactic stage. This is the classic "AMITT Framework" that's bundled with MISP.  The [clickable](amitt_red_framework_clickable.html) version is for rapidly creating lists of TTPs. 
* [AMITT Blue Team Framework](amitt_blue_framework.md) - Disinformation responder TTPs, listed by tactic stage. These are countermeasures, listed by the earliest tactic stages they're likely to be used in. 

AMITT OBJECTS: all the entities used to create the Red Team and Blue Team frameworks: 
* [Phases](phases_index.md): higher-level groupings of tactics, created so we could check we didn't miss anything
* [Tactics](tactics_index.md): stages that someone running a misinformation incident is likely to use
* [Techniques](techniques_index.md): activities that might be seen at each stage
* [Tasks](tasks_index.md): things that need to be done at each stage.  In Pablospeak, tasks are things you do, techniques are how you do them. 
* [Counters](counters_index.md): countermeasures to AMITT TTPs.  
* [Actors](actors_index.md): resources needed to run countermeasures
* [Response types](responsetype_index.md): the course-of-action categories we used to create counters
* [Metatechniques](metatechniques_index.md): a higher-level grouping for countermeasures
* [Incidents](incidents_index.md): incident descriptions used to create the AMITT frameworks

There's a directory for each of these, containing a datasheet for each individual entity (e.g. [technique T0046 Search Engine Optimization](techniques/T0046.md)).  There's also a directory [generated_csvs](generated_csvs) containing any CSV files we generate from the above tables. 

## UPDATING AMITT

**MAJOR CHANGES** Any major changes to AMITT models are agreed on by CogSecCollab, then added by the AMITT design authorities - currently SJ Terp and Pablo Breuer. 

**MINOR CHANGES** YOU, yes, you, CAN ADD INFORMATION TO ANY AMITT OBJECT FILE
* The details above "DO NOT EDIT ABOVE THIS LINE" are generated and will be overwritten every time we run the update code; anything you write above that line will be lost
* The details below "DO NOT EDIT ABOVE THIS LINE" are saved every time we run the update code. You can safely add notes below that line. 

We love any and all suggestions for improvements, comments and offers of help - either reach out to us using [this google form](https://docs.google.com/forms/d/e/1FAIpQLSdZuyKFp1UZzk6qUE4IN1O14HaJ-F4TH9thxR3hrRU-Mu7QUQ/viewform), or if you're comfortable with Github, add to this repo's [issues list](https://github.com/cogsec-collaborative/AMITT/issues) or fork the repo with corrections. (We're also going back through the [original issues list](https://github.com/misinfosecproject/amitt_framework/issues))

## Using the Raw Data file

AMITT is open source.  If you want to do your own thing with AMITT data, these will help:
* all the master data for it is in directory [AMITT_MASTER_DATA](AMITT_MASTER_DATA). Look for the [AMITT_TTPs_MASTER.xlsx](AMITT_MASTER_DATA/AMITT_TTPs_MASTER.xlsx) spreadsheet. This contains disinformation creators' tactics, techniques, tasks, phases, and counters. 

* The [AMITT TTP Guide](https://docs.google.com/document/d/1Kc0O7owFyGiYs8N8wSq17gRUPEDQsD5lLUL_3KGCgRE/edit#) has more detailed information on each technique. 

* The code to create all the HTML datasheets is in directory [HTML_GENERATING_CODE](HTML_GENERATING_CODE): you'll need generate_amitt_ttps.py and all the template files. 

If you have your own version of this repository and update AMITT_TTPs_MASTER.xlsx, typing "python generate_amitt_ttps.py" will update all the files above from it. 


## Who's Responsible for AMITT

* **[CogSecCollab](http://cogsec-collab.org/)** maintains and updates the AMITT family of models: AMITT-STIX, the AMITT Red framework (of disinformation creation), and the AMITT Blue framework (of disinformation countermeasures and mitigations). We've used AMITT in the CTI League's Covid19 responses, and tested it in trials with NATO, the EU, and several other countries' disinformation units. Pablo Breuer and SJ Terp are the current design authorities for the AMITT models.

* **MisinfosecWG**, aka the Credibility Coalition's [Misinfosec working group](https://github.com/credcoalition/community-site/wiki/Working-Groups) created the original AMITT frameworks. The Red Framework was started in December 2018, and refined in a Credibility Coalition Misinfosec seminar; the Blue Framework was started as a collection of potential disinformation countermeasures, at a Coalition Misinfosec seminar in November 2019. CogSecCollab is the nonprofit that spun out of MisinfosecWG. 

* **Everyone who contributes to AMITT** (and there are many of you). Thank you to everyone who contributes to AMITT, and has contributed to AMITT over the years. 

* **You**. Thank you for being here.

AMITT is licensed under [CC-BY-4.0](LICENSE.md)
