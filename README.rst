
Tools for TI speech synthesizers
================================

Hello. Please, press, a code number.

Chips supported
---------------

Texas Instruments has made several hardware revisions of their speech synthesiser; each with slightly different lookup tables for pitch, energy and weighting.

- TMS5100/TMC0281 (1st gen. Speak & Spell)
- TMS5110/TMC0281D (2nd gen. Speak & Spell, Chrysler EVA, some arcade boards)
- TMC0280/CD2801 (Speak & Math, Speak & Read, Language Translator)
- TMS5200 (TI 99/4 Speech Module, Bally pinball audio boards)
- TMS5220/TMS5220C/TMS5220CNL (lots of arcade boards and microcomputer expansion cards)

Acknowledgements
----------------

The LPC encoder is a Python port of `BlueWizard <https://github.com/patrick99e99/bluewizard>`_ by Patrick J. Collins / Collinator Studios Inc, made available under the MIT License.

The PCM decoder is a hacked up copy of `MAME's <https://github.com/mamedev/mame>`_ TMS5220 chip emulator, by Frank Palazzolo, Aaron Giles, Jonathan Gevaryahu, Raphael Nabet, Couriersud and Michael Zapf, made available under the BSD License.
