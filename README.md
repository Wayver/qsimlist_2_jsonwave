# qsimlist_2_jsonwave

I created this script to translate simulation waveform data contained in a
QuestaSIM .lst file into a format for input to : https://wavedrom.com/editor.html

You can view a brief sample of the .lst format at **https://metacpan.org/pod/ModelSim::List**

The right-hand side of the image on page thirty of https://www.microsemi.com/document-portal/doc_view/136365-modelsim-me-10-4c-gui-reference-manual-for-libero-soc-v11-7 shows the "matrix-esque" waveform that I wanted to avoid taking screenshots of.

By writing a .lst file, running it through the script, and feeding the output JSON to wavedrom, you can obtain a cleaner and higher resolution image.
