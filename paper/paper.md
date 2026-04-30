---
title: 'TACtool: A targeting and co-ordination tool for spatial sampling and data traceability applied to scanning electron microscopy and laser ablation ICP-MS'
tags:
  - Python
  - Laser ablation
  - Traceability
  - Microanalysis
  - Targeting
  - Coordination
authors:
  - name: Leo Rudczenko
    corresponding: true
    orcid: 0009-0005-8941-1387
    affiliation: 1
  - name: Connor. J. Newstead
    orcid: 0009-0006-2349-7461
    affiliation: "1, 2"
  - name: Matthew Horstwood
    orcid: 0000-0003-4200-8193
    affiliation: 1
  - name: John Stevenson
    orcid: 0000-0002-2245-1334
    affiliation: 1
affiliations:
  - name: British Geological Survey, Keyworth, Nottingham, UK.
    index: 1
  - name: University of Surrey, Surrey, UK.
    index: 2
date: 14 January 2026
bibliography: paper.bib
---

# Summary

The precise analysis of geological samples is crucial for understanding the history of Earths formation, identification of mineral deposits, age dating, paleoclimatology and more [@Chew:2021]. Laser ablation inductively coupled plasma mass spectrometry (LA-ICP-MS) has become one of the most common analytical techniques for the chemical analysis of such geological samples by measuring elemental composition upon ablation of target areas, often performed on mineral grains at the micron scale [@George:2018; @Yao:2017; @Astbury:2018]. Accurate recording of laser ablation targets is important for traceability, ensuring that collected data can be matched to its target location and any other related data. Annotation of laser ablation targets or Regions Of Interest (ROI) for laser ablated samples can be mapped onto high resolution Scanning Electron Microscope (SEM) images, which are often used for mineral characterisation [@Astbury:2018; @Bonnetti:2020]. Historically, this has been a manual process for many laboratories, thus could lead to inaccurate labelling which impedes traceability, verification of conclusions, and compromises important studies.

# Statement of Need

TACtool (Targeting And Coordination tool) is a PyQt based desktop application which was designed to enable users to annotate laser ablation analysis locations onto high resolution SEM images. TACtool records pixel coordinates of annotations which can be uploaded to laser ablation systems, ensuring efficient and accurate re-coordination of target locations relative to the spatial context resolved in the SEM image. In the latest version, TACtool can also import an SEM image and identity point coordinates and plot these existing positions onto the imported image. These can then be used or added to ready for export. This automatic process additionally saves time, lab resources, and therefore money, when identifying ROI. TACtool also provides optional metadata recording for every ROI which further improves reproducibility and traceability throughout a lab's workflow.

The intuitive and accessible front-end design of TACtool allows users with a lack of computational experience to easily record their annotations. The software can be downloaded as a compiled program, mitigating the need to setup complex development environments. This simplicity continues throughout the workflow within TACtool. Users can import an image file onto a canvas, before clicking directly onto that image to add their ROI and respective annotations. The coordinates and metadata for each ROI can be exported to a plain text Comma-Separated Values (CSV) file, ready to be uploaded directly to an ESI laser ablation system.

# State of the Field

There exists tools for the annotation of geological samples and integration with laser ablation systems, however they all have varying functionality, accessibility and ease of use (\autoref{tab:table1}).

|Software|Description|Access|
|---|---|---|
|GeoStar μGIS TM [@GeoStar]|Manual and automatic sample point selection. Image importation from any source such as SEM. Integration with ICP-MS systems and automatic instrument control.|Proprietary software package written for use in RESOlution instruments and requires a paid license.|
|ImageJ (FIJI) [@ImageJ]|Many available plugins and features allow customization of the software to perform a variety of tasks.|Free and open source.|
|Quartz PCI [@QuartzPCI]|PCI allows for SEM image annotation and measurement of features.|Requires a paid license.|
|uScope Navigator [@uScopeNavigator]|Capable of image processing such as gamma, contrast and bilateral smoothing filters in addition to ROI annotation. May not be compatible with all laser ablation systems.|Requires a paid license/comes with their microscope systems.|
|MIPAR [@MIPAR]|Capable of analysing SEM images and creating annotations with locations recorded.|Requires a paid license.|
|PIBC [@PIBC]|A plugin for QGIS which provides tools to import SEM images and associated metadata.|Free and open source.|

Table: \label{tab:table1}

Many of the existing paid software solutions are efficient, but the fact that they are paid for restricts their use within the community, both financially and through dependency on manufacturer systems in the case of proprietary software. Moreover, ImageJ and PIBC are free and provide a range of customization options, but the complexity of this customization requires specialist time investment, making it difficult for those with less computational experience. This leaves a niche for a simple, accessible, and free to use solution, which enables efficient laser ablation workflows. In this body of work, we believe our software, TACtool, is a contribution to this niche. TACtool was designed to be an accessible standalone application, built to solve a single problem in a user-friendly interface. No setup is required, as the application can be downloaded as a compiled program, ready to use with any instrument. Being free and open source means that TACtool is open to everybody with no restrictions.

# Software Design

When designing and building TACtool, there were 3 main goals we aimed for. Firstly, we wanted to produce a front-end application that is lightweight and easy to use, whilst still providing useful traceability. To fulfil this, we have included a very limited number of settings which allow some customisation and sample metadata entry. TACtool can then export the ROI and associated metadata to a simple CSV file, in a format which is recognised by ESI laser ablation systems. Secondly, Python and the PyQt library was chosen to develop the code, as Python is widely used in the scientific community, and the underlying Qt library is widely used to build graphical user interfaces. Using what is already widely known allows others in the community to more easily contribute to the TACtool code. Thirdly, TACtool was to be distributed as a single executable, with no setup required by the end user. We used GitHub Actions to achieve this by setting up an automated pipeline which takes the latest version of the code and compiles it. We are then able to provide a single download button in the README document, making it as simple as possible for end users to get started.

# Research Impact Statement

The community surrounding TACtool has been growing since it's initial release, as shown by the download metrics from GitHub (\autoref{fig:figure_1}). Many recent changes to the software originate from community feedback, including bug fixes, the addition of the transparent ghost point for easier ROI identification (v1.3.0), and a MacOS version of the software to accommodate a new user base (v1.2.0). This feedback came from GitHub issues and discussions at LA-ICP-MS conferences.

![TACtool download metrics as of 2026/01/14. Executable downloads are provided by GitHub releases and their statistics via the GitHub API.
\label{fig:figure_1}](release_downloads_tactool.png)

Although TACtool was initially created for geological samples, it has possible applications for many other fields requiring spatial coordination and re-cordination of disparate, spatially correlated data sets. The use cases of TACtool are scale independent and as a standalone user environment, TACtool is platform agnostic with outputs that can be used with any downstream instrumentation able to use the output information. This wider use is promoted by the fact that TACtool is open source and free to use, making it excellent for any community requiring its use, and enabling individuals to contribute to further features and adapting it for their own specific needs.

TACtool offers a laser ablation annotation and coordinate system solution to any community requiring use at no cost and with maximum accessibility in mind, increasing laboratory efficiency, traceability of data and their interpretation, and therefore scientific reproducibility.

# AI Usage Disclosure

No AI tools have been used at any point in the process of developing this software, writing the documentation, or writing this paper itself.

# Acknowledgements

This work was supported by the British Geological Survey via NERC national capability. For the purpose of open access, the author has applied a Creative Commons Attribution (CC BY) licence to any Author Accepted Manuscript version arising.

# References
