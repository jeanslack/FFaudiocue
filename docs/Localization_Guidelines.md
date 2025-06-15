
# Localization Guidelines

Help to translate FFaudiodplit to other languages
-----------------

## Updates an existing translation

#### Requirements:
- [GNU gettext](https://www.gnu.org/software/gettext), to build `.mo` file.
- [poEdit](https://poedit.net/), to do the actual translation I recommend poEdit,
it allows you to create or update a translation catalog, for instance, a `.po` file from
a `.pot` file.

> There is a bit of difference between [.po file format (portable object)](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html)
> and [.pot file format (portable object template)](https://help.phrase.com/help/gettext-template-pot-files).
> Specifically, the [ffaudiocue.pot](https://github.com/jeanslack/FFaudiodplit/blob/main/ffaudiocue/locale/ffaudiocue.pot)
> file is just a template that contains the new strings not yet translated and should
> never be modified directly. The [ffaudiocue.po](https://github.com/jeanslack/FFaudiodplit/blob/main/ffaudiocue/locale/it_IT/LC_MESSAGES/ffaudiocue.po)
> file can instead be edited for translation and updated with the latest strings
> not yet translated, see below.

- Download [latest source](https://github.com/jeanslack/FFaudiodplit/archive/refs/heads/main.zip) of FFaudiodplit

- Extract the archive and navigate inside the obtained folder.

- Browse into the `ffaudiocue/locale` folder, then choose the language folder to translate.

- Locate `ffaudiocue.po` file related to your language, example:

``` text
    FFaudiodplit (rootdir)
    |__ ffaudiocue
        |__ locale
            |__ it_IT
                |__ LC_MESSAGES
                    |__ ffaudiocue.po
```
- Open the `ffaudiocue.po` file with [poEdit](https://poedit.net/)

- Click on [poEdit](https://poedit.net/) menu bar *-> Catalog -> Update from POT file...*, then
import the `ffaudiocue.pot` file template sited on `locale` folder. This is **important** as it
ensures that the `ffaudiocue.po` file is fully updated with the latest translation strings.

- Also, check the catalog property data on menu bar *> Catalog > Property...*
and make sure it contains at least some updated information you could provide.

- Now, you are ready to start your translation. When you're done save your work;
you can always resume your work from where you left off.

- Before running FFaudiodplit to test your updated translation, Make sure that
[Python3](https://www.python.org/), [wxPython](https://www.wxpython.org/),
[PyPubSub](https://pypubsub.readthedocs.io/en/v4.0.3/), [ffcuesplitter](https://pypi.org/project/ffcuesplitter/).
are installed.

- Try your new tranlation by open a terminal window, `cd` on the `FFcuespitter-GUI`
sources folder and type: `python3 launcher`.

When you have completed your translation with 'PoEdit', please [Create a new pull
request](https://github.com/jeanslack/FFaudiodplit/pulls) or send me your
`ffaudiocue.po` file at: <jeanlucperni@gmail.com>

I will be grateful!!

At your disposal for clarification.

-----------------

## Start with a new translation
{: .bg-green-300}

If you are not familiar with the command line and some applications described below, STOP!
Contact me and describe me in which language you want to translate FFcuespitter-GUI. I will provide
everything you need, so that you can only open [poEdit][poEdit](https://poedit.net/)
and start your new translation.

#### Requirements
- [GNU gettext](https://www.gnu.org/software/gettext) (To build `.pot` and the
`.mo` files)
- [poEdit](https://poedit.net/), to do the actual translation I recommend poEdit,
it allows you to create or update a translation catalog, for instance, a `.po` file from
a `.pot` file.
- Some kind of text editor to edit some code (notepad++, nano, Mousepad etc are sufficient)

> Note: The instructions below assume basic knowledge of the command line (OS independent)
{: .fs-4 .text-grey-dk-100}

- To start a new translation, download [here](https://github.com/jeanslack/FFaudiodplit/archive/refs/heads/main.zip)
latest FFcuespitter-GUI snapshot, then unzip the archive.

- In this example we assume that the new language to be translated is **German**.

- Then, browse the new FFcuespitter-GUI folder and create two new folders: `de_DE` folder
and within which a `LC_MESSAGES` folder, like following tree:

```text
    FFcuespitter-GUI (rootdir)
    |__ ffaudiocue
        |__ locale
            |__ de_DE
                |__ LC_MESSAGES
```

- Copy the `ffaudiocue.pot` file translation template located in the `/locale`
folder, and paste into the `LC_MESSAGES` folder.

- Rename it to change extension name to `ffaudiocue.po` .

- Now open the `ffaudiocue.po` with [poEdit](https://poedit.net/), check the catalog
property data on menu bar *> Catalog > Property...* and make sure it contains at least
some updated information you could provide.

- Now, you are ready to start your new translation. When you're done save your work;
you can always resume your work from where you left off. This generates (compile) a file called
`ffaudiocue.mo` with your new native language tanslation.

- Before running FFcuespitter-GUI to test your new translation, Make sure that
[Python3](https://www.python.org/), [wxPython](https://www.wxpython.org/),
[PyPubSub](https://pypubsub.readthedocs.io/en/v4.0.3/), [ffcuesplitter](https://pypi.org/project/ffcuesplitter/)
are installed.

- Open the `FFcuespitter-GUI/ffaudiocue/ffc_sys/app_const.py` file with your favorite
text-editor and append the newly translated language line, for example:

```python
    "de": wx.LANGUAGE_GERMAN,
```

to:

```python
    supLang = {"en": wx.LANGUAGE_ENGLISH,
               "it": wx.LANGUAGE_ITALIAN,
               "de": wx.LANGUAGE_GERMAN,
               }
```

- For a list of the supported languages to append on `app_const.py`, please see
[wx.Language](https://wxpython.org/Phoenix/docs/html/wx.Language.enumeration.html#wx-language)

- When finish save `app_const.py` .

- Try your new tranlation by open a terminal window, `cd` on the `FFcuespitter-GUI`
sources folder and type: `python3 launcher`

When you have completed your new translation, please [Create a new pull
request](https://github.com/jeanslack/FFaudiodplit/pulls) or send me your
`ffaudiocue.po` file at: <jeanlucperni@gmail.com>

I will be grateful!!
